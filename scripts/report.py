"""Generate derived inventories and a standalone HTML report from a scan."""
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
import html
import json
import re
from common import read_json, save_json, safe_child

def jsonl(path):
    with Path(path).open(encoding='utf-8') as stream:
        for line in stream:
            if line.strip(): yield json.loads(line)

def build_report(out,profile):
    out=Path(out)
    raw=out/'raw'
    scan=read_json(raw/'scan-summary.json')
    metadata=read_json(raw/'metadata-manifest.json')
    archives=read_json(raw/'archives.json')
    registries=read_json(raw/'registries.json')
    installation=read_json(out/'installation-files.json')
    extracted={m['path']:safe_child(raw,m['output']) for m in metadata if m['status']=='extracted'}
    errors=[]
    project={}
    for name,path in extracted.items():
        if name.endswith('.uproject'):
            try: project=read_json(path)
            except Exception as ex: errors.append({'path':name,'error':str(ex)})
    declarations={p['Name']:p for p in project.get('Plugins',[])}
    manifest={}
    for name,path in extracted.items():
        if name.endswith('.upluginmanifest'):
            try:
                for item in read_json(path).get('Contents',[]):
                    manifest[item['File'].removeprefix('../../../')]=item['Descriptor']
            except Exception as ex: errors.append({'path':name,'error':str(ex)})
    files=list(jsonl(raw/'files.jsonl'))
    project_prefix=profile['project']+'/Content/'
    content=defaultdict(lambda:{'files':0,'packages':0})
    maps=[]
    extensions=Counter()
    for f in files:
        path=f['path']; ext=PurePosixPath(path).suffix.lower(); extensions[ext]+=1
        if path.lower().startswith(project_prefix.lower()):
            rest=path[len(project_prefix):]
            if '/' in rest:
                folder=rest.split('/')[0];content[folder]['files']+=1
                content[folder]['packages']+=int(ext in ('.uasset','.umap'))
        if ext=='.umap': maps.append({'path':path,'archive':f['archive'],'evidence':'directory index extension'})
    classes=Counter(); mounts=Counter(); asset_count=0; native_refs=defaultdict(set)
    registry_packages=set()
    blueprints=[]
    for reg in registries:
        if reg['status']!='parsed':continue
        for a in jsonl(safe_child(raw,reg['output'])):
            asset_count+=1;classes[a['assetClass']]+=1;registry_packages.add(a['package'])
            pieces=a['package'].split('/')
            if len(pieces)>1:mounts[pieces[1]]+=1
            for value in a['tags'].values():
                for module in re.findall(r'/Script/([A-Za-z0-9_]+)\.',value):native_refs[module].add(a['package'])
            if 'Blueprint' in a['assetClass']:
                blueprints.append({'package':a['package'],'class':a['assetClass'],'parent':a['tags'].get('ParentClass'),'nativeParent':a['tags'].get('NativeParentClass'),'interfaces':a['tags'].get('ImplementedInterfaces')})
    plugins=[]
    for name,path in extracted.items():
        if not name.endswith('.uplugin'):continue
        try: descriptor=read_json(path)
        except Exception as ex: errors.append({'path':name,'error':str(ex)});continue
        plugin=PurePosixPath(name).stem; modules=descriptor.get('Modules',[])
        refs=set().union(*(native_refs.get(m['Name'],set()) for m in modules)) if modules else set()
        plugins.append({'name':plugin,'scope':'Project' if name.lower().startswith(profile['project'].lower()+'/') else 'Engine','version':descriptor.get('VersionName',''),'author':descriptor.get('CreatedBy',''),'description':descriptor.get('Description',''),'moduleTypes':sorted({m['Type'] for m in modules}),'modules':modules,'explicitEnabled':declarations.get(plugin,{}).get('Enabled'),'declaration':declarations.get(plugin),'enabledByDefault':descriptor.get('EnabledByDefault'),'descriptorPath':name,'inManifest':name in manifest,'manifestEqual':manifest.get(name)==descriptor,'registryEntries':mounts.get(plugin,0),'registryReferencingPackages':len(refs),'dependencies':descriptor.get('Plugins',[]),'descriptor':descriptor})
    plugins.sort(key=lambda p:(p['scope'],p['name'].lower()))
    folders=[{'name':k,**v} for k,v in sorted(content.items())]
    binaries=[x for x in installation if PurePosixPath(x['path']).suffix.lower() in ('.dll','.exe')]
    components=defaultdict(list)
    for f in binaries:
        path=f['path']
        if '/Plugins/' in path or path.startswith('RemappedPlugins/'):
            prefix=re.split(r'/(?:Binaries|ThirdParty|Source)/',path,maxsplit=1)[0]
            components[prefix].append(path)
    loose=[{'path':k,'files':v,'evidence':'loose binary paths; plugin descriptor unavailable unless separately listed'} for k,v in sorted(components.items())]
    encrypted=sum(a['encryptedIndex'] for a in archives)
    missing=[a for a in archives if a['hasDirectoryIndex'] and not a['mounted']]
    metadata_failures=[m for m in metadata if m['status']!='extracted']
    status='blocked-encrypted-indexes' if not files and encrypted else 'partial' if missing or metadata_failures or errors or any(r['status']!='parsed' for r in registries) else 'indexed'
    summary={
        'name':profile['name'],'project':profile['project'],'profile':scan['profile'],
        'versionEvidence':profile['version_evidence'],'engineAssociation':project.get('EngineAssociation') or None,
        'status':status,'containerFiles':dict(Counter(PurePosixPath(x['path']).suffix.lower() for x in installation if PurePosixPath(x['path']).suffix.lower() in ('.pak','.utoc','.ucas'))),
        'archiveReaders':scan['archiveReaders'],'mountedReaders':scan['mountedReaders'],'encryptedIndexReaders':encrypted,
        'effectiveFiles':len(files),'rawIndexEntries':sum(a['entries'] for a in archives),'encryptedIndexedFiles':scan['encryptedIndexedFiles'],
        'pluginDescriptors':len(plugins),'projectPlugins':sum(p['scope']=='Project' for p in plugins),'enginePlugins':sum(p['scope']=='Engine' for p in plugins),
        'manifestEntries':len(manifest),'explicitEnabled':sum(p.get('Enabled') is True for p in declarations.values()),'explicitDisabled':sum(p.get('Enabled') is False for p in declarations.values()),
        'contentFolders':len(folders),'registryEntries':asset_count,'registryUniquePackages':len(registry_packages),'registryStatus':'parsed' if any(r['status']=='parsed' for r in registries) else 'parse-error' if registries else 'not-found-in-readable-indexes',
        'mapPaths':len(maps),'metadataExtracted':len(extracted),'metadataUnavailable':len(metadata_failures),'metadataParseErrors':len(errors),'extensionCounts':dict(extensions),'looseBinaryFiles':len(binaries),'looseComponentPaths':len(loose),'projectModules':project.get('Modules',[])
    }
    for filename,data in [('summary.json',summary),('plugins.json',plugins),('content-folders.json',folders),('maps.json',maps),('blueprints.json',blueprints),('classes.json',dict(classes.most_common())),('project-plugin-declarations.json',list(declarations.values())),('loose-components.json',loose),('loose-binaries.json',binaries),('metadata-parse-errors.json',errors),('module-references.json',{k:sorted(v) for k,v in native_refs.items()})]:save_json(out/filename,data)
    notes=["Présence dans un index, manifeste ou dossier ≠ module chargé en jeu.","Une version de compatibilité CUE4Parse n'est pas une preuve indépendante de la version exacte du moteur.","Les compteurs de chemins incluent les fichiers compagnons. Les archives optionnelles et patchs peuvent partager des chemins ; l'index effectif suit la priorité du fournisseur."]
    if not asset_count:notes.append("Aucun registre exploitable : les classes et parents de Blueprints ne sont pas inférés à partir du nom des fichiers.")
    if encrypted:notes.append(f"{encrypted} lecteurs signalent un index chiffré. Les compteurs nuls ne signifient pas que le jeu ne contient aucun asset ou plugin.")
    if metadata_failures:notes.append(f"{len(metadata_failures)} métadonnées indisponibles ; voir raw/metadata-manifest.json.")
    rows='\n'.join(f"| {p['name']} | {p['version']} | {', '.join(p['moduleTypes'])} |" for p in plugins if p['scope']=='Project')
    md=f"# {profile['name']} — inventaire local\n\nProfil : `{scan['profile']}`. {profile['version_evidence']}\n\nÉtat : **{status}**.\n\n"
    md+=f"- {len(files):,} chemins effectifs ; {sum(a['entries'] for a in archives):,} entrées dans les index individuels.\n- {len(plugins)} descripteurs : {summary['projectPlugins']} projet, {summary['enginePlugins']} moteur.\n- {len(folders)} dossiers racines de contenu ; {len(maps)} chemins .umap.\n- {len(extracted)} métadonnées extraites ; {len(metadata_failures)} indisponibles.\n- {asset_count:,} entrées de registre analysées.\n- {len(binaries)} binaires livrés hors archives.\n\n"
    md+='\n'.join('- '+n for n in notes)+'\n\n'
    if rows:md+='## Plugins du projet\n\n| Nom | Version déclarée | Types de modules |\n|---|---|---|\n'+rows+'\n\n'
    md+='## Résultats\n\n[Explorateur](explorer.html) · [Plugins](plugins.json) · [Contenu](content-folders.json) · [Composants hors archives](loose-components.json) · [Déclarations du projet](project-plugin-declarations.json) · [Index complet](raw/all-paths.txt) · [Métadonnées et erreurs](raw/metadata-manifest.json) · [Journal du parseur](raw/parser.log)\n'
    (out/'RAPPORT.md').write_text(md,encoding='utf-8')
    compact=[{k:p[k] for k in ['name','scope','version','author','description','moduleTypes','explicitEnabled','descriptorPath']} for p in plugins]
    payload=json.dumps({'summary':summary,'plugins':compact,'folders':folders,'maps':maps,'binaries':binaries,'classes':[{'name':k,'count':v} for k,v in classes.most_common()]},ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TITLE</title><style>body{background:#11181d;color:#e0ebf2;font:15px system-ui;margin:0}main{max-width:1450px;margin:auto;padding:35px}h1{font-size:34px}p{color:#a8bdca;line-height:1.6}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats div{background:#20313a;padding:20px;border-radius:8px}.stats b{display:block;font-size:28px}a{color:#8bdbc1}.controls{display:flex;gap:10px;margin:25px 0;flex-wrap:wrap}button,input,select{background:#20313a;border:1px solid #4b626f;padding:10px;border-radius:5px;color:inherit;font:inherit}button{cursor:pointer}input{flex:1;min-width:250px}table{width:100%;border-collapse:collapse;table-layout:auto}td,th{padding:12px;border-bottom:1px solid #314550;text-align:left;overflow-wrap:anywhere}small{display:block;color:#9cb2bf}.notice{border-left:3px solid #e5bc76;padding:15px;background:#202b31}</style><main><h1>TITLE</h1><p id="profile"></p><div class="stats" id="stats"></div><p class="notice">NOTES</p><p><a href="RAPPORT.md">Rapport</a> · <a href="plugins.json">Descripteurs détaillés</a> · <a href="raw/all-paths.txt">Tous les chemins</a> · <a href="raw/metadata-manifest.json">Métadonnées / erreurs</a> · <a href="loose-components.json">Composants hors archives</a></p><div class="controls"><button data-view="plugins">Plugins</button><button data-view="folders">Contenu</button><button data-view="maps">Cartes</button><button data-view="binaries">Binaires livrés</button><button data-view="classes">Classes du registre</button><select id="scope"><option value="all">Tous les plugins</option><option>Project</option><option>Engine</option></select><input id="query" placeholder="Rechercher" aria-label="Rechercher"></div><p id="count"></p><table><thead id="head"></thead><tbody id="body"></tbody></table></main><script id="data" type="application/json">DATA</script><script>
const data=JSON.parse(document.getElementById('data').textContent),s=data.summary;let view='plugins';const q=document.getElementById('query'),scope=document.getElementById('scope'),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));document.getElementById('profile').textContent=s.profile+' · '+s.versionEvidence;document.getElementById('stats').innerHTML=[[s.effectiveFiles,'chemins lisibles'],[s.pluginDescriptors,'descripteurs'],[s.contentFolders,'dossiers'],[s.mapPaths,'chemins .umap'],[s.registryEntries,'entrées de registre']].map(([n,l])=>`<div><b>${n.toLocaleString('fr-FR')}</b>${l}</div>`).join('');
function render(){let rows=data[view].filter(r=>JSON.stringify(r).toLowerCase().includes(q.value.toLowerCase()));scope.hidden=view!=='plugins';if(view==='plugins'&&scope.value!=='all')rows=rows.filter(r=>r.scope===scope.value);const total=rows.length;rows=rows.slice(0,500);let headers,cells;if(view==='plugins'){headers=['Nom / description','Version / auteur','Portée / modules','Déclaration'];cells=rows.map(r=>[esc(r.name)+'<small>'+esc(r.description)+'</small>',esc(r.version)+'<small>'+esc(r.author)+'</small>',esc(r.scope)+'<small>'+esc(r.moduleTypes.join(', '))+'</small>',r.explicitEnabled===true?'Enabled=true':r.explicitEnabled===false?'Enabled=false':'Non déclaré']);}else if(view==='folders'){headers=['Dossier','Fichiers','Packages .uasset/.umap'];cells=rows.map(r=>[esc(r.name),r.files,r.packages]);}else if(view==='maps'){headers=['Chemin','Archive'];cells=rows.map(r=>[esc(r.path),esc(r.archive)]);}else if(view==='binaries'){headers=['Chemin livré','Octets'];cells=rows.map(r=>[esc(r.path),r.bytes.toLocaleString('fr-FR')]);}else{headers=['Classe','Entrées'];cells=rows.map(r=>[esc(r.name),r.count]);}document.getElementById('head').innerHTML='<tr>'+headers.map(h=>'<th>'+h+'</th>').join('')+'</tr>';document.getElementById('body').innerHTML=cells.map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('');document.getElementById('count').textContent=total+' résultats'+(total>500?' (500 affichés ; affiner la recherche)':'');}q.oninput=scope.onchange=render;document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{view=b.dataset.view;render()});render();</script></html>'''
    page=page.replace('</style>','table{table-layout:fixed}th:first-child{width:42%}th:nth-child(2){width:22%}th:nth-child(3){width:20%}td:last-child{word-break:normal;overflow-wrap:normal}td small{overflow-wrap:anywhere}</style>')
    page=page.replace('TITLE',html.escape(profile['name'])+' / inventaire').replace('NOTES','<br>'.join(html.escape(n) for n in notes)).replace('DATA',payload)
    (out/'explorer.html').write_text(page,encoding='utf-8')
    return summary
