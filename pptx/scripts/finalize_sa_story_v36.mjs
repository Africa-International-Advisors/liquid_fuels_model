import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill='C:/Users/ITafr/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const qa=root+'/pptx/qa/story_v36';
const source=root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v31.pptx';
await fs.mkdir(qa+'/final',{recursive:true});
const result=await finalizePresentation({workspaceDir:root,
 candidatePath:qa+'/with_chart_workbooks.pptx',
 finalPath:qa+'/final/SA_Market_Story_2026-10-11_v36.pptx',
 pythonExecutable:runtime+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','11588750,6858000','--validate-heading-fit'],
 fontPolicy:{basis:'reference',families:['Lato'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},
 // Native Office reopening and HasSmartArt checks replace an artifact-tool import,
 // which is not needed to validate the requested package's native diagrams.
 verifyArtifactToolImport:false,receiptPath:qa+'/validation.json'});
console.log(JSON.stringify(result).slice(0,1200));
