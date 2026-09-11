using CUE4Parse.FileProvider;
using CUE4Parse.UE4.AssetRegistry;
using CUE4Parse.UE4.Readers;
using CUE4Parse.UE4.Versions;
using CUE4Parse.UE4.VirtualFileSystem;
using CUE4Parse.Compression;
using CUE4Parse.Encryption.Aes;
using CUE4Parse.UE4.Objects.Core.Misc;
using Serilog;
using System.Security.Cryptography;
using System.Text.Json;

if (args.Length != 3 || !Enum.TryParse<EGame>(args[2], out var game))
{
    Console.Error.WriteLine("Usage: UnrealInventory PaksDirectory EmptyOutputDirectory CUE4ParseGameEnum");
    Console.Error.WriteLine("An optional local AES key map can be provided by UE_INVENTORY_AES_FILE (JSON GUID -> hex key). Keys are never written to reports.");
    return 2;
}
var input = Path.GetFullPath(args[0]);
var output = Path.GetFullPath(args[1]);
if (!Directory.Exists(input)) throw new DirectoryNotFoundException(input);
if (output.Equals(input, StringComparison.OrdinalIgnoreCase) || output.StartsWith(input + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
    throw new ArgumentException("Output cannot be inside the game archive directory");
Directory.CreateDirectory(output);
if (Directory.EnumerateFileSystemEntries(output).Any()) throw new ArgumentException("Use an empty output directory for a fresh scan");
var jsonOptions = new JsonSerializerOptions { WriteIndented = true };
void Save(string name, object value) => File.WriteAllText(Path.Combine(output, name), JsonSerializer.Serialize(value, jsonOptions));
Log.Logger = new LoggerConfiguration().MinimumLevel.Information().WriteTo.File(Path.Combine(output,"parser.log")).CreateLogger();
try { OodleHelper.Initialize(Environment.GetEnvironmentVariable("UE_INVENTORY_OODLE")); }
catch (Exception ex) { Log.Warning("Oodle initialization unavailable: {Message}", ex.Message); }
using var provider = new DefaultFileProvider(input, SearchOption.TopDirectoryOnly, new VersionContainer(game), StringComparer.OrdinalIgnoreCase);
provider.Initialize();
var registered = provider.UnloadedVfs.ToArray();
var diagnostics = new List<object>();
var expected = Directory.EnumerateFiles(input).Where(p => Path.GetExtension(p).ToLowerInvariant() is ".pak" or ".utoc").ToArray();
foreach (var path in expected.Where(p => !registered.Any(r => r.Name.Equals(Path.GetFileName(p), StringComparison.OrdinalIgnoreCase))))
    diagnostics.Add(new { stage="registration", archive=Path.GetFileName(path), error="Reader not registered; see parser.log" });
var fallbackMounted = new HashSet<IAesVfsReader>();
try { provider.Mount(); }
catch (Exception ex)
{
    diagnostics.Add(new {stage="provider-mount",error=ex.Message});
    Log.Warning(ex,"Global mount failed; attempting directory indexes independently");
    foreach (var reader in registered.Where(r => r.HasDirectoryIndex && !provider.MountedVfs.Contains(r)))
    {
        if (reader.IsEncrypted && provider.CustomEncryption == null) continue;
        try { reader.MountTo(provider.Files, StringComparer.OrdinalIgnoreCase); fallbackMounted.Add(reader); }
        catch (Exception failure) { diagnostics.Add(new {stage="directory-mount",archive=reader.Name,error=failure.Message}); }
    }
}
var aesFile = Environment.GetEnvironmentVariable("UE_INVENTORY_AES_FILE");
if (!string.IsNullOrEmpty(aesFile))
{
    var keys = JsonSerializer.Deserialize<Dictionary<string,string>>(File.ReadAllText(aesFile))!;
    foreach (var pair in keys) provider.SubmitKey(new FGuid(pair.Key), new FAesKey(pair.Value));
}
var mounted = provider.MountedVfs.Concat(fallbackMounted).ToHashSet();
var readers = registered.Concat(provider.MountedVfs).Concat(provider.UnloadedVfs).Distinct().OrderBy(r => r.Name).ToArray();
var archives = readers.Select(r => new {
    name = r.Name, mounted = mounted.Contains(r), encryptedIndex = r.IsEncrypted,
    hasDirectoryIndex = r.HasDirectoryIndex, entries = r.FileCount,
    encryptedFiles = r.EncryptedFileCount, mountPoint = r.MountPoint,
    compression = r.CompressionMethods.Select(c => c.ToString()).ToArray(),
    encryptionGuid = r.EncryptionKeyGuid.ToString()
}).ToArray();
Save("archives.json",archives);
Directory.CreateDirectory(Path.Combine(output,"indexes"));
foreach (var reader in readers)
{
    var filename = string.Concat(reader.Name.Select(c => Path.GetInvalidFileNameChars().Contains(c) ? '_' : c));
    using var index = new StreamWriter(Path.Combine(output,"indexes",filename+".jsonl"));
    foreach (var entry in reader.Files.Values.OrderBy(f => f.Path,StringComparer.Ordinal))
        index.WriteLine(JsonSerializer.Serialize(new { path=entry.Path, bytes=entry.Size, encrypted=entry.IsEncrypted, compression=entry.CompressionMethod.ToString() }));
}
var files = provider.Files.Values.OrderBy(f => f.Path,StringComparer.Ordinal).ToArray();
using (var index = new StreamWriter(Path.Combine(output,"files.jsonl")))
using (var paths = new StreamWriter(Path.Combine(output,"all-paths.txt")))
    foreach (var file in files)
    {
        index.WriteLine(JsonSerializer.Serialize(new {path=file.Path,bytes=file.Size,encrypted=file.IsEncrypted,compression=file.CompressionMethod.ToString(),archive=(file as VfsEntry)?.Vfs.Name}));
        paths.WriteLine(file.Path);
    }
var metadata = new List<object>();
var registryStats = new List<object>();
var metadataExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "uplugin","uproject","upluginmanifest","ini","modules","target" };
var metadataRoot = Path.Combine(output,"metadata");
Directory.CreateDirectory(metadataRoot);
foreach (var file in files.Where(f => metadataExtensions.Contains(f.Extension) || f.Name.Equals("AssetRegistry.bin",StringComparison.OrdinalIgnoreCase) || f.Name.Equals("DevelopmentAssetRegistry.bin",StringComparison.OrdinalIgnoreCase) || f.Name=="Build.version"))
{
    string status="extracted"; string? error=null; string? hash=null; long bytes=0;
    string? relativeTarget=null;
    try
    {
        var target=Path.GetFullPath(Path.Combine(metadataRoot,file.Path.Replace('/',Path.DirectorySeparatorChar)));
        if (!target.StartsWith(metadataRoot+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unsafe archive path");
        if (file.Size>512L*1024*1024) throw new InvalidDataException("Metadata exceeds 512 MiB per-file limit");
        if (file.IsEncrypted && string.IsNullOrEmpty(aesFile)) status="encrypted-no-key";
        else
        {
            var data=file.Read();
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.WriteAllBytes(target,data);
            relativeTarget=Path.GetRelativePath(output,target).Replace('\\','/');
            bytes=data.LongLength;
            hash=Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
            if (file.Name.EndsWith("AssetRegistry.bin",StringComparison.OrdinalIgnoreCase))
            {
                try
                {
                    using var archive=new FByteArchive(file.Name,data,new VersionContainer(game));
                    var registry=new FAssetRegistryState(archive);
                    var assetPath=Path.Combine(output,"registry-"+registryStats.Count+".jsonl");
                    using var writer=new StreamWriter(assetPath);
                    foreach (var asset in registry.PreallocatedAssetDataBuffers)
                        writer.WriteLine(JsonSerializer.Serialize(new {package=asset.PackageName.ToString(),name=asset.AssetName.ToString(),assetClass=asset.AssetClass.ToString(),tags=asset.TagsAndValues.ToDictionary(kv=>kv.Key.ToString(),kv=>kv.Value),chunks=asset.ChunkIDs,flags=asset.PackageFlags.ToString()}));
                    registryStats.Add(new {path=file.Path,status="parsed",assets=registry.PreallocatedAssetDataBuffers.Length,dependsNodes=registry.PreallocatedDependsNodeDataBuffers.Length,packageData=registry.PreallocatedPackageDataBuffers.Length,output=Path.GetFileName(assetPath)});
                }
                catch (Exception ex) { registryStats.Add(new {path=file.Path,status="parse-error",error=ex.ToString()}); }
            }
        }
    }
    catch (Exception ex) { status="read-error"; error=ex.Message; }
    metadata.Add(new {path=file.Path,archive=(file as VfsEntry)?.Vfs.Name,status,bytes,sha256=hash,output=relativeTarget,error});
}
Save("metadata-manifest.json",metadata);
Save("registries.json",registryStats);
Save("scan-diagnostics.json",diagnostics);
var summary = new {profile=game.ToString(),profileValue=(int)game,archiveReaders=readers.Length,mountedReaders=mounted.Count,effectiveFiles=files.Length,encryptedIndexedFiles=files.Count(f=>f.IsEncrypted),metadataCandidates=metadata.Count,registries=registryStats.Count,requiredKeyGuids=provider.RequiredKeys.Select(g=>g.ToString()).ToArray()};
Save("scan-summary.json",summary);
Console.WriteLine(JsonSerializer.Serialize(summary,jsonOptions));
Log.CloseAndFlush();
return 0;
