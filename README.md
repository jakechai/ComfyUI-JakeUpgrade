## ComfyUI Jake Upgrade

A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow customization by Jake.  
Feel free to join my [Discord server](https://discord.gg/2XC3w9as2f).  
If you like what I share, please support me with [PayPal](https://paypal.me/jakechaikefu).

> [!NOTE]
> - ComfyUI frontend starts the [deprecation process of Group node](https://github.com/Comfy-Org/ComfyUI_frontend/issues/3441#issuecomment-2814386708) in v1.17. Please stay in v1.15 for now until they release the [Subgraph](https://github.com/Comfy-Org/rfcs/blob/subgraph/rfcs/0000-subgraph.md), which replaces Group node. "embeded python.exe" -m pip install --force-reinstall comfyui-frontend-package==1.15.12
> - ComfyUI frontend breaks the Impact-Pack Switch(Any) node. Though it's been fixed in the latest version(v8.12), but it only supports comfyui-frontend-package>=1.16.9. Please switch Impact-Pack to v8.8.1 In the ComfyUI Manager which works fine with Group node while comfyui-frontend-package==1.15.12. 

Here's my other product [UI for ComfyUI API](https://chaikefu.gumroad.com/l/ComfyAPIUI) using my ComfyUI API workflow.  
Please check the [video](https://youtu.be/eyjy10T201M).  
<a href="https://youtu.be/eyjy10T201M" target="_blank">
 <img src="https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/ComfyUIAPIUI.png" alt="UI for ComfyUI API" />
</a>

## Changelog
<details>
<summary><b>Previous Version</b></summary>
	
	- 2024-06-23 - v1.0.0	released.  
	- 2024-07-11 - v1.0.6	Noise Injection for Upscale Workflow.  
	- 2024-07-16 - v1.0.7	Single Image to Mesh Workflow updated.  
	- 2024-07-21 - v1.0.8	Orbit Poses Constant nodes added. 3 Image to Mesh Workflows updated.  
	- 2024-07-22 - v1.0.9	3DGS workflow added.  
	- 2024-07-24 - v1.1.0	img2mesh workflow updated. Craftsman Mesh added. 
				Three OrbitPoses nodes been added to 3D-Pack.  
	- 2024-07-31 - v1.1.1	Prompt Combine node added.  
	- 2024-08-03 - v1.1.2	Resize to Focus added to image2mesh workflow.  
	- 2024-08-21 - v1.1.3	Random Beats node added (not for AIGC).  
	- 2024-09-01 - v1.2.0	SD3 workflow added. Noise Injection (Inspire) added. 
				Refine, Upscale, and Detailer process major updated. 
				SD15 Hand Fix supports SDXL and SD3 workflow. 
				SDXL IPAdapter supports SD3 workflow. 
				NoiseInjection Component and workflow added.  
	- 2024-09-04 - v1.2.1	In/Out Paint ControlNet Component added. 
				Inpaint Module Workflow updated. 
				SD15|SDXL|SD3 Workflow updated. 
				Image Remove Alpha JK node added.  
	- 2024-09-05 - v1.2.2	Black Pixel switch added for Inpaint ControlNet Component following ControlNet Preprocessor AUX Custom Node's update.  
	- 2024-09-06 - v1.2.3	Refinement Noise Injection added. 
				txt2prompt and img2prompt workflow added. 
				img2prompt component added.  
	- 2024-09-07 - v1.2.4	img2mesh workflow doesn't need _JK.pack, so that doesn't need to install segment anything, VLM nodes, and IF AI tools.  
	- 2024-09-09 - v1.2.5	Clip l, clip g, t5xxl texture encode logic upgrade. 
				Clip l & g switch added. 
				Negative g switch added. 
				SDXL Clip Text Encode Target Resolution Scale added.  
	- 2024-09-10 - v1.2.6	detailer: add detail lora.  
	- 2024-09-11 - v1.2.7	Magic Photo Prompter added.  
	- 2024-09-13 - v1.2.8	Use Comfy UI default set union controlnet type to load xinsir sdxl controlnet union.  
				Remove Inspire Pack and WAS Nodes Suite in img2mesh workflows. 
				Group Node Image RemBG added, using InSPYReNet TransparentBG from Essentials to remove background and Image Composite Masked to add grayscale background.  
	- 2024-09-15 - v1.2.9	Inpaint Simple updated. Outpaint Simple added. 
				txt2img | img2img | inpaint workflow updated. 
				In/Out Paint to Refinement process added. 
				Upscale to Refinment process added.  
	- 2024-09-21 - v1.3.0	Inpaint/Outpaint Latent | Checkpoint | ControlNet group nodes updated. 
				Inpaint and txt2img/img2img workflows updated. 
				SD3/Flux Inpaint ControlNet added.  
	- 2024-09-24 - v1.3.1	Hand Fix Detailer upgrades, supports SD15 | SDXL | Flux. 
				SD3 Hand Fix need to choose SDXL models for the InstantX Depth ControlNet does not work properly. 
				Replace SD3 ControlNet Apply with new ControlNet Apply Node.  
	- 2024-09-25 - v1.3.2	AIO Preprocessor added for txt2img | img2img workflow.  
				Detailer, Upscale workflows updated. Refine workflow added.  
	- 2024-09-26 - v1.3.3	Latent Noise Mask switch added for Inpaint/Outpaint ControlNet. 
				Specified Dual Clip switch added for sdxl workflow.  
	- 2024-09-28 - v1.3.4	Hand Fix supports SD3 and Flux. Hand Fix module workflow added.
	- 2024-09-29 - v1.3.5	Inpaint Group Nodes upgrade, add more Image | Mask | Latent control.
	- 2024-10-01 - v1.3.6	Inpaint Group Nodes upgrade, change color grading method.
	- 2024-10-03 - v1.3.7	Remove Outpaint Pad Feathering.
	- 2024-10-06 - v1.4.0	Replace Base Ipadapter simple with IPAdapter Style and Composition Transfer in SD15 and SDXL workflow.
				SD3 Aspect Ratio node and SD3 Base Model Parameter node added. 
				SD3 Api workflow added to make up the shorcomings of SD3 local deployment using Stability SD3 control and inpaint nodes.
	- 2024-10-10 - v1.5.0	Flux KSampler and Flux Ksampler Adv group nodes added.
				Flux txt2img and img2img workflow added. Flux KSampler workflow added.
				Inpaint/Outpaint ControlNet and Checkpoint method order changed.
				Enchance and Resize Input Image added for img2img workflow.
				Noise | Guider | Sampler | Sigmas switch added.
	- 2024-10-10 - v1.5.1	Fal LLM and VLM API added for prompt generation workflow and SAI API workfkow.
	- 2024-10-11 - v1.5.2	Flux KSampler Adv updated, use SplitSigmas instead of SplitSigmasDenoise.
	- 2024-10-19 - v1.6.0	Image Generation group node and module workflow added.
				Switch Model and CLIP JK🐉 node removed.
				Rename Apply ControlNet Stack SD3 to Applly ControlNet VAE.
				Tiling Mode and Empty Latent Color nodes added.
	- 2024-11-08 - v1.7.0	Normal | Input version of Image Gen and Image Gen Adv group nodes added.
				Krita workflow added using Input version of Image Gen group nodes.
				Remove Comfyroll Custom Nodes from the must-have-node list.
				ControlNet Apply and ControlNet Stack nodes upgraded, supports Union, Alimama Inpaint.
				ControlNet Stack Input Switch node added.
				Add Blend with Original Mask option to Inpaint, Image Gen Adv and Image Gen Input group nodes.
				IsMaskEmpty Node and Image Crop by Mask Group Node added.
	- 2024-12-24 - v1.8.0	1. Add SAI API Replace Background and Relight. Add missing parameters of SAI API nodes.
				2. Add Detail Daemon Custom Nodes to most of image|mesh generation workflows and group nodes.
				3. Add SDXL Target Res JK🐉 node to fix SDXL Text Encode Target Resolution not working.
				4. Add Image | Latent Crop by Mask, Resize, Crop by Mask and Resize, Stitch nodes. Add Crop and Stitch operation for Image Gen and Inpaint Group Nodes.
				5. Update img2mesh MV upscale method to achieve better results: SD15 img2img + SDXL Refine + Ultimate Upscale.
				6. Add Bool_Or and Bool_And nodes for workflows need to be group. Replace Bool Binary Operation node (Or as default) with Bool_Or.
				7. Add Color Grading Node.
				8. Seperate Multi-ControlNet Stack node to ControlNet Loader and Multi-ControlNet Param Stack.
				9. Add "None" selection as default to IPAdapter Unified Loader for better workflow control, especially in API mode.
				10. Add Image Refine Group Node.
				11. Krita image generation workflows updated.
				12. Add Krita Refine, Upscale and Refine, Hand fix, CN preprocessor, remove bg and SAI API module series.
				13. Remove JK🐉::Pad Image for Outpainting. Remove JK🐉::CLIPSegMask group node, replace it with Essentials CLIPSeg node.
				14. Remove [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui) and [Layer Style](https://github.com/chflame163/ComfyUI_LayerStyle) Custom Node from must-have-list for their complexity.
				15. Remove useless Group Nodes: JK🐉::Image to Prompt (LLava Local), JK🐉::Image to Prompt Advanced (LLava Local), JK🐉::SegAnythingMask, JK🐉::txt2img.
				16. SD3 | Flux image generation workflow | group nodes support Stop At Clip Layer (needs ComfyUI v0.3.8up).
	- 2024-12-27 - v1.8.5	1. Add new Detailer Module.
				2. Add new image generation workflow.
				3. Fix Krita HandFix workflow bug.
	- 2025-01-03 - v1.8.6	1. ControlNet image supports alpha. Add A1111-ControlNet-like effective mask for ControlNet (Stack) Apply nodes.
				2. Load Image With Alpha, Make Image Grid, and Split Image Grid nodes added.
				3. IF AI nodes recreated.
				4. ComfyUI API workflow added.
				5. Get Mesh 3D data workflow added.
	- 2025-01-10 - v1.8.8	1. Add ControlNet Effective Mask switch for all Image Generation Group Nodes.
				2. Fix image resolution bug of Image Generation adv group nodes.
				3. First Comfy Org Registry version.
	- 2025-02-04 - v1.9.0	1. Add Inject Latent Noise to advanced imgen group nodes.
				2. Fix the Input Mask logic of advanced imgen group nodes.
				3. Add "SD3 Prompts switch" for SD3 imgen group nodes.
				4. Switch clip l and g bug fix.
				5. Follow the update of Inspire-Pack Random Noise node for imgen group nodes.
				6. Image Generation | API | Kirta workflows updated.
	- 2025-02-08 - v1.9.1	1. Add Stop At Clip Layer to image refine group nodes.
				2. Add Flux Guidance to common imgen | refine group nodes.
				3. Add ComfyUI API workflows: controlnet preprocessor | upscale | refine.
	- 2025-02-17 - v1.9.2	1. Update JK_module_Mesh-Get_3D_data module workflow.
				2. Imgen SDXL API workflow bug fixed.
				3. Add checkpoint version flux API workflows.
				4. Add image grid API workflows.
	- 2025-02-20 - v1.9.3	1. Update IPAdapter nodes along with the Main branch.
				2. Add Discord server.
	- 2025-02-24 - v1.9.4	1. Update Mesh-Get 3D data workflow along with the Load 3D node.
				2. Update auto-prompt workflows along with the Flux Prompt Generater node.
	- 2025-02-27 - v1.9.5	1. Add new parameters to SAI API nodes.
				2. All SAI API nodes have been approved by [ComfyUI SAI API](https://github.com/Stability-AI/ComfyUI-SAI_API) and been removed from replacement folder..
				3. Update IPAdapter nodes along with the Main branch.
	- 2025-03-13 - v1.9.6	1. Save MVs/CCMs/Depths/Images in both png and exr for img2mesh workflows. Add Load png|exr switch.
				2. Add Get OrbitPoses From List JK🐉 node. Replace Get CamPoses From List node of 3D Pack.
				3. Fix HandFix workflow issue.
				4. Update Get Mesh 3D Data workflow using the new Load 3D Node.
	- 2025-03-22 - v1.9.7	1. CR TriMesh Input Switch JK🐉 added for Hunyuan 3D Wrapper workflow.
				2. Add Hunyuan 3D Wrapper img2mesh workflow.
				3. Updage MV upscale and refine process for img2mesh workflow.
	- 2025-04-05 - v1.9.8	1. Cleaning up the codes.
				2. UI for ComfyUI API released.
				3. Update Seamless Texture workflow.
	- 2025-05-09 - v1.9.9	1. Add Florence 2 to Auto Prompt Workflow.
				2. Add Segment Anything 2 to Detailer Workflow.
				3. Add Flux Fill to Flux imgen group node and workflow.
				4. Add RoughOutline_JK node to generate motion outline.
				5. Add OpenDWPose_JK node to combine openpose and dwpose.
				6. Add Wan Video main workflow and module workflows.
	- 2025-05-11 - v1.9.10	1. Update Wan Video repaint workflows.
	- 2025-05-12 - v1.9.11	1. Add Wan Video VACE ff/flf2vid repaint workflows.
	- 2025-05-12 - v1.9.12	1. Update Wan Video VACE workflow.
</details>

- 2025-05-18 - v1.9.13
1. Update Wan Video VACE workflow.

- 2025-05-20 - v1.9.14
1. Add Trim Video Latent Node ot Native Wan VACE workflow. Update Native t2v and r2v Wan VACE workflow.
2. Remove Save Image and Save Webm nodes for Auto Mask | Auto Motion | Control Video Module workflow. Video Combine can save as both.

- 2025-05-29 - v1.9.15
1. Use 10 camera for Hy3D MV Sampling by default.
2. Add Mesh MV sample generation module workflow using IG2MV, MV Adapter and Stable X Delight.
3. Add Multi-GPU version of Wan Video Generation workflows.
4. Add the Wan Vace 14B fp16 model to the model list instruction.

- 2025-06-02 - v1.9.16
1. Add Dilated ControlNet for Wan Video t2v workflows.
2. Add Canny & HED Control Video generation methods for Dilated ControlNet.
3. Add ATI Trajectory generation method to Video-Auto Motion module.
4. Add Save|Load StringListToJSON nodes to save|load ATI Trajectory presets.
5. Use bf16 Wan Video VAE by default for all Wan Video generation workflows.
6. Add Multi-GPU version of Flux Image Generation workflow.

## Installation
1. `git clone https://github.com/jakechai/ComfyUI-JakeUpgrade` into the `custom_nodes` folder 
    - e.g. `custom_nodes\ComfyUI-JakeUpgrade`
	
	OR: Install using ComfyUI Manager.
2. Open a Command Prompt/Terminal/etc.
3. Change to the `custom_nodes\ComfyUI-JakeUpgrade` folder you just created 
    - e.g. `cd C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-JakeUpgrade`
4.  Install python packages
      - **Windows Standalone installation** (embedded python):
	  
        `../../../python_embeded/python.exe -s -m pip install -r requirements.txt`
	    
		OR: run install.bat.
      - **Manual/non-Windows installation**
	  
        `pip install -r requirements.txt`

## Copy files in the replacement folder(optional)

- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) : Copy `_JK.pack` to `...\ComfyUI\user\default\ComfyUI-Manager\components` for saving all JK Group Nodes within each workflow file.
- [Prompt Stylers](https://github.com/wolfden/ComfyUi_PromptStylers) : Copy and replace files to `custom_nodes\ComfyUi_PromptStylers` for new styles.
- [IP Adapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus) : (Workaround before IPAdapter approves my pull request) Copy and replace files to `custom_nodes\ComfyUI_IPAdapter_plus` for better API workflow control by adding "None" selection.

> [!NOTE]
> - Group Nodes can be copied and pasted between workflows in the latest ComfyUI. See details in my Video Introduction of Group Nodes.
> - Load [All JK (Group) Nodes](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/All%20Nodes-JK.json) for all JK Group Nodes.
> - These replacement files cause the node conflict warning in the ComfyUI Manager. But don't worry, JakeUpgrade never loaded them.

## Update
1. ComfyUI Manager - Fetch Update - Search JakeUpgrade and Update.
2. ComfyUI Manager - Custom Nodes Manager - Search JaKeUpgrade and Try Update (If method 1 fails).
3. Change to `custom_nodes\ComfyUI-JakeUpgrade` folder, open cmd or PowerShell, type `git pull`  (If method 1 & 2 fails).

> [!NOTE]
> - Files in the replacement folder need to be updated by hand if needed.

## Video Introduction
- Wan Video | Wan Vace workflows: [Youtube](https://youtu.be/4KNOufzVsUs) | [Bilibili](https://www.bilibili.com/video/BV1kCJGzgEL4/)
- Wan Video update 1(Dilated CN | ATI | Uni3C preview): [Youtube](WIP) | [Bilibili](WIP)
- img2mesh Hunyuan3D Wrapper workflow: [Youtube](https://youtu.be/g94Jufz9Znw) | [Bilibili](https://www.bilibili.com/video/BV1w7ZMY2Ehp/) | [portable ComfyUI v0.3.27+pytorch 2.5.1+cuda 12.4](https://drive.google.com/file/d/1rUchssRRdqLQtu0A-OCkKKLU8_bd0y8q/view?usp=sharing)
- img2mesh Hunyuan3D Add more MV texture samples: [Youtube](https://www.youtube.com/watch?v=hdMAksRD9jM)
- 1.8.x Update(Group Nodes | Detail Daemon | Crop and Stitch | Stop At Clip Layer  | ControlNet Efficiency Mask | ControlNet Loader | "None" selection for IPAdapter Loader| Imgen workflows | API workflows | Krita workflows | Get Mesh 3D data): [Youtube](https://youtu.be/pwHsGnn0zsg) | [Bilibili](https://www.bilibili.com/video/BV1J3cuenEE2/)
- txt2img&img2img workflow: [Youtube](https://www.youtube.com/watch?v=PKnxhFZNu2c) | [Bilibili](https://www.bilibili.com/video/BV1h6421f7AQ/)
- txt2img&img2img SD3 workflow: [Youtube](https://youtu.be/MZBNzaWHdr8) | [Bilibili](https://www.bilibili.com/video/BV1ceHheqEru/)
- txt2img&img2img API workflow: [Youtube](https://www.youtube.com/watch?v=4DWWUQij9jM) | [Bilibili](https://www.bilibili.com/video/BV1QR1BYUE5r/)
- Group Nodes - Image Generation and Krita workflow: [Youtube](https://youtu.be/tOy0ve2cgaQ) | [Bilibili](https://www.bilibili.com/video/BV1GXUVYRE2k/)
- Prompts Switch: [Youtube](https://youtu.be/M8lVr1lP82U) | [Bilibili](https://www.bilibili.com/video/BV1ZRNwerEev/)
- prompt generation workflow: [Youtube](https://youtu.be/h_2PimL3iXY) | [Bilibili](https://www.bilibili.com/video/BV1FZp4ebEjK/)
- inpaint workflow: [Youtube](https://www.youtube.com/watch?v=A9nABNizMdY) | [Bilibili](https://www.bilibili.com/video/BV1wd4ge8EQf/)
- img2mesh workflow: [Youtube](https://www.youtube.com/watch?v=CbG2Vq3kps0) | [Bilibili](https://www.bilibili.com/video/BV1CE4m1R7br/)
- 3D-Pack Installation Tips：[Youtube](https://www.youtube.com/watch?v=RjuoLMCpvbI) | [Bilibili](https://www.bilibili.com/video/BV1Nm421375F/)
- 3D-Pack Algorithm Comparison：[Youtube](https://www.youtube.com/watch?v=E7Oj8UUGLic) | [Bilibili](https://www.bilibili.com/video/BV1CU411U7y4/)
- Seamless Texture: [Youtube](https://youtu.be/ExPUbiRkJo0) | [Bilibili](https://www.bilibili.com/video/BV1UZ42187Gq/)

## JakeUpgrade Workflow

### ComfyUI

#### Workflow
- [JK_workflow_imgen_SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_SD15.json)
- [JK_workflow_imgen_SD15 legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_SD15_legacy.json)
- [JK_workflow_imgen_SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_SDXL.json)
- [JK_workflow_imgen_SDXL legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_SDXL_legacy.json)
- [JK_workflow_imgen_SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_SD3.json)
- [JK_workflow_imgen_SD3 legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_SD3_legacy.json)
- [JK_workflow_imgen_Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_Flux.json)
- [JK_workflow_imgen_Flux_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_Flux_mGPU.json)
- [JK_workflow_imgen_Flux legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_Flux_legacy.json)
- [JK_workflow_imgen_API](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_imgen_API.json)
- [JK_workflow_img2mesh_Hunyuan3DWrapper](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_img2mesh_Hunyuan3DWrapper.json)
- [JK_workflow_img2mesh_CRM&Zero123plus&MVDream&CharacterGen](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_img2mesh_CRM&Zero123plus&MVDream&CharacterGen.json)
- [JK_workflow_img2mesh_Unique3D&Wonder3D&Era3D](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_img2mesh_Unique3D&Wonder3D&Era3D.json)
- [JK_workflow_img2mesh_Zero123&SV3D](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_img2mesh_Zero123&SV3D.json)
- [JK_workflow_img2mesh_3DGS](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_img2mesh_3DGS.json)
- [JK_workflow_Video-Wan_txt2vid](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_txt2vid.json)
- [JK_workflow_Video-Wan_txt2vid_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_txt2vid_mGPU.json)
- [JK_workflow_Video-Wan_img2vid_ref](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_img2vid_ref.json)
- [JK_workflow_Video-Wan_img2vid_ref_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_img2vid_ref_mGPU.json)
- [JK_workflow_Video-Wan_img2vid_flf](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_img2vid_flf.json)
- [JK_workflow_Video-Wan_img2vid_flf_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_img2vid_flf_mGPU.json)
- [JK_workflow_Video-Wan_vid2vid](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_vid2vid.json)
- [JK_workflow_Video-Wan_vid2vid_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan_vid2vid_mGPU.json)
- [JK_workflow_Video-Wan__VACE](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan__VACE.json)
- [JK_workflow_Video-Wan__VACE_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan__VACE_mGPU.json)
- [JK_workflow_Video-Wan__SkyreelDF](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan__SkyreelDF.json)
- [JK_workflow_Video-Wan__SkyreelDF_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-Wan__SkyreelDF_mGPU.json)
- [JK_workflow_Video-FramePack](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Main/JK_workflow_Video-FramePack.json)

#### Module
- [JK_module_00_AutoPrompt](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_00_AutoPrompt.json)
- [JK_module_01_Image Generation](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_01_ImgGen.json)
- [JK_module_01_Image Generation Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_01_ImgGen_Adv.json)
- [JK_module_04_Refine](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_04_Refine.json)
- [JK_module_04_Refine legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_04_Refine_legacy.json)
- [JK_module_05_Upscale 1st](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_05_Upscale_1st.json)
- [JK_module_05_Upscale 1st legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_05_Upscale_1st_legacy.json)
- [JK_module_05_Upscale 2nd](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_05_Upscale_2nd.json)
- [JK_module_06_Detailer](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_06_Detailer.json)
- [JK_module_06_Detailer legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_06_Detailer_legacy.json)
- [JK_module_06_HandFix](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_06_HandFix.json)
- [JK_module_06_HandFix legacy](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_06_HandFix_legacy.json)
- [JK_module_07_Inpaint](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_07_Inpaint.json)
- [JK_module_NoiseInjectionVariation](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_NoiseInjectionVariation.json)
- [JK_module_Concept](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Concept.json)
- [JK_module_Seamless Texture](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Seamless%20Texture.json)
- [JK_module_Flux_KSampler](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_FluxKSampler.json)
- [JK_module_Mesh-ReMesh_Projection](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Mesh-ReMesh_Projection.json)
- [JK_module_Mesh-Get_3D_data](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Mesh-Get_3D_data.json)
- [JK_module_Mesh-Gen18MVTex](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Mesh-Gen18MVTex.json)
- [JK_module_Video-AutoMask](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-AutoMask.json)
- [JK_module_Video-AutoMotion](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-AutoMotion.json)
- [JK_module_Video-AutoPrompt](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-AutoPrompt.json)
- [JK_module_Video-Control](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-Control.json)
- [JK_module_Video-Upscale&Interpolation](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-Upscale&Interpolation.json)
- [JK_module_Video-Upscale&Interpolation_mGPU](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-Upscale&Interpolation_mGPU.json)
- [JK_module_Video-WanExplanation](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/Module/JK_module_Video-WanExplanation.json)

#### API
- [JK_API_Imgen_SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Imgen_SD15.json)
- [JK_API_Imgen_SD15 dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20SD15.json)
- [JK_API_Imgen_SD15 params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20SD15-params.py)
- [JK_API_Imgen_SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Imgen_SDXL.json)
- [JK_API_Imgen_SDXL dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20SDXL.json)
- [JK_API_Imgen_SDXL params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20SDXL-params.py)
- [JK_API_Imgen_SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Imgen_SD3.json)
- [JK_API_Imgen_SD3 dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20SD3.json)
- [JK_API_Imgen_SD3 params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20SD3-params.py)
- [JK_API_Imgen_Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Imgen_Flux.json)
- [JK_API_Imgen_Flux dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20Flux.json)
- [JK_API_Imgen_Flux params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20Flux-params.py)
- [JK_API_Imgen_Flux_ckpt](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Imgen_Flux_ckpt.json)
- [JK_API_Imgen_Flux_ckpt dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20Flux%20Ckpt.json)
- [JK_API_Imgen_Flux_ckpt params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Imgen%20Flux%20Ckpt-params.py)
- [JK_API_Refine_SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Refine_SD15.json)
- [JK_API_Refine_SD15 dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20SD15.json)
- [JK_API_Refine_SD15 params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20SD15-params.py)
- [JK_API_Refine_SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Refine_SD3.json)
- [JK_API_Refine_SD3 dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20SD3.json)
- [JK_API_Refine_SD3 params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20SD3-params.py)
- [JK_API_Refine_Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Refine_Flux.json)
- [JK_API_Refine_Flux dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20Flux.json)
- [JK_API_Refine_Flux params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20Flux-params.py)
- [JK_API_Refine_Flux_ckpt](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_Refine_Flux_ckpt.json)
- [JK_API_Refine_Flux_ckpt dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20Flux%20Ckpt.json)
- [JK_API_Refine_Flux_ckpt params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20Refine%20Flux%20Ckpt-params.py)
- [JK_API_ControlNet_Preprocessor](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_ControlNet_Preprocessor.json)
- [JK_API_ControlNet_Preprocessor dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20ControlNet%20Preprocessor.json)
- [JK_API_ControlNet_Preprocessor params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20ControlNet%20Preprocessor-params.py)
- [JK_API_TP_MakeImageGrid](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_TP_MakeImageGrid.json)
- [JK_API_TP_MakeImageGrid dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20TP%20MakeImageGrid.json)
- [JK_API_TP_MakeImageGrid params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20TP%20MakeImageGrid-params.py)
- [JK_API_TP_SplitImageGrid](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/JK_API_TP_SplitImageGrid.json)
- [JK_API_TP_SplitImageGrid dev](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20TP%20SplitImageGrid.json)
- [JK_API_TP_SplitImageGrid params](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/ComfyUI/API/dev/JK%20API%20TP%20SplitImageGrid-params.py)

> [!NOTE]
> - You need ComfyUI v0.3.8up to use SD3 | Flux Image Gen workflows.
> - ComfyUI API workflows are workflows created to allow other software to call ComfyUI, which include non-dev editable workflows and dev-for-call workflows, as well as python files with supporting parameters.
> - Installing a separate version of ComfyUI to work with 3D Pack is recommended.   
> - ComfyUI-3D-Pack 3DMesh | 3DGS Preview works with the new frontend of ComfyUI with a [restriction](https://github.com/MrForExample/ComfyUI-3D-Pack/issues/343#issuecomment-2423478072).  

### Krita (sync)

#### Workflow
- [JK_workflow-Krita Common](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20Common.json)
- [JK_workflow-Krita Common Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20Common%20Adv.json)
- [JK_workflow-Krita SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20SD15.json)
- [JK_workflow-Krita SD15 Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20SD15%20Adv.json)
- [JK_workflow-Krita SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20SDXL.json)
- [JK_workflow-Krita SDXL Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20SDXL%20Adv.json)
- [JK_workflow-Krita SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20SD3.json)
- [JK_workflow-Krita SD3 Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20SD3%20Adv.json)
- [JK_workflow-Krita Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20Flux.json)
- [JK_workflow-Krita Flux Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Main/JK_workflow-Krita%20Flux%20Adv.json)

#### Module
- [JK_module-Krita RemBG](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20RemBG.json)
- [JK_module-Krita CN preprocessor](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20CN%20preprocessor.json)
- [JK_module-Krita HandFix Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20HandFix%20Flux.json)
- [JK_module-Krita HandFix SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20HandFix%20SD3.json)
- [JK_module-Krita HandFix SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20HandFix%20SD15.json)
- [JK_module-Krita HandFix SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20HandFix%20SDXL.json)
- [JK_module-Krita Refine Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20Refine%20Flux.json)
- [JK_module-Krita Refine SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20Refine%20SD3.json)
- [JK_module-Krita Refine SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20Refine%20SD15.json)
- [JK_module-Krita Refine SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20Refine%20SDXL.json)
- [JK_module-Krita UpscaleRefine Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20UpscaleRefine%20Flux.json)
- [JK_module-Krita UpscaleRefine SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20UpscaleRefine%20SD3.json)
- [JK_module-Krita UpscaleRefine SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20UpscaleRefine%20SD15.json)
- [JK_module-Krita UpscaleRefine SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/Module/JK_module-Krita%20UpscaleRefine%20SDXL.json)

#### SAI
- [JK_SAI-Krita Gen Core-txt2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Gen%20Core-txt2img.json)
- [JK_SAI-Krita Gen SD3-img2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Gen%20SD3-img2img.json)
- [JK_SAI-Krita Gen SD3-txt2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Gen%20SD3-txt2img.json)
- [JK_SAI-Krita Gen Ultra-img2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Gen%20Ultra-img2img.json)
- [JK_SAI-Krita Gen Ultra-txt2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Gen%20Ultra-txt2img.json)
- [JK_SAI-Krita Ctrl-Sketch](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Ctrl-Sketch.json)
- [JK_SAI-Krita Ctrl-Structure](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Ctrl-Structure.json)
- [JK_SAI-Krita Ctrl-Style](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Ctrl-Style.json)
- [JK_SAI-Krita Edit-Erase](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Edit-Erase.json)
- [JK_SAI-Krita Edit-RemBG](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Edit-RemBG.json)
- [JK_SAI-Krita Edit-Repaint](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Edit-Repaint.json)
- [JK_SAI-Krita Edit-ReplaceBGAndRelight](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Edit-ReplaceBGAndRelight.json)
- [JK_SAI-Krita Edit-SearchAndRecolor](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Edit-SearchAndRecolor.json)
- [JK_SAI-Krita Edit-SearchAndReplace](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Edit-SearchAndReplace.json)
- [JK_SAI-Krita Upscale-Conservative](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Upscale-Conservative.json)
- [JK_SAI-Krita Upscale-Creative](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Upscale-Creative.json)
- [JK_SAI-Krita Upscale-Fast](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Krita/SAI/JK_SAI-Krita%20Upscale-Fast.json)

### Krita (dev)

#### Workflow
- [JK Workflow Krita Common](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20Common.json)
- [JK Workflow Krita Common Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20Common%20Adv.json)
- [JK Workflow Krita SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20SD15.json)
- [JK Workflow Krita SD15 Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20SD15%20Adv.json)
- [JK Workflow Krita SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20SDXL.json)
- [JK Workflow Krita SDXL Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20SDXL%20Adv.json)
- [JK Workflow Krita SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20SD3.json)
- [JK Workflow Krita SD3 Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20SD3%20Adv.json)
- [JK Workflow Krita Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20Flux.json)
- [JK Workflow Krita Flux Adv](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Workflow%20Krita%20Flux%20Adv.json)

#### Module
- [JK Module Krita RemBG](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20RemBG.json)
- [JK Module Krita CN Preprocessor](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20CN%20Preprocessor.json)
- [JK Module Krita HandFix Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20HandFix%20Flux.json)
- [JK Module Krita HandFix SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20HandFix%20SD3.json)
- [JK Module Krita HandFix SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20HandFix%20SD15.json)
- [JK Module Krita HandFix SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20HandFix%20SDXL.json)
- [JK Module Krita Refine Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20Refine%20Flux.json)
- [JK Module Krita Refine SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20Refine%20SD3.json)
- [JK Module Krita Refine SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20Refine%20SD15.json)
- [JK Module Krita Refine SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20Refine%20SDXL.json)
- [JK Module Krita UpscaleRefine Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20UpscaleRefine%20Flux.json)
- [JK Module Krita UpscaleRefine SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20UpscaleRefine%20SD3.json)
- [JK Module Krita UpscaleRefine SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20UpscaleRefine%20SD15.json)
- [JK Module Krita UpscaleRefine SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20Module%20Krita%20UpscaleRefine%20SDXL.json)

#### SAI
- [JK SAI Krita Gen Core-txt2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Gen%20Core-txt2img.json)
- [JK SAI Krita Gen SD3-img2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Gen%20SD3-img2img.json)
- [JK SAI Krita Gen SD3-txt2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Gen%20SD3-txt2img.json)
- [JK SAI Krita Gen Ultra-img2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Gen%20Ultra-img2img.json)
- [JK SAI Krita Gen Ultra-txt2img](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Gen%20Ultra-txt2img.json)
- [JK SAI Krita Ctrl-Sketch](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Ctrl-Sketch.json)
- [JK SAI Krita Ctrl-Structure](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Ctrl-Structure.json)
- [JK SAI Krita Ctrl-Style](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Ctrl-Style.json)
- [JK SAI Krita Edit Erase](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Edit%20Erase.json)
- [JK SAI Krita Edit RemBG](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Edit%20RemBG.json)
- [JK SAI Krita Edit Repaint](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Edit%20Repaint.json)
- [JK SAI Krita Edit Replace BG and Recolor](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Edit%20Replace%20BG%20and%20Recolor.json)
- [JK SAI Krita Edit Search And Recolor](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Edit%20Search%20And%20Recolor.json)
- [JK SAI Krita Edit Search And Replace](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Edit%20Search%20And%20Replace.json)
- [JK SAI Krita Upscale-Conservative](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Upscale-Conservative.json)
- [JK SAI Krita Upscale-Creative](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Upscale-Creative.json)
- [JK SAI Krita Upscale-Fast](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/replacement/krita/ai_diffusion/workflows/JK%20SAI%20Krita%20Upscale-Fast.json)

> [!NOTE]
> - Installing a separate version of ComfyUI to work with Krita is recommended.
> - [Krita AI Plugin - ComyUI Custom Workflows](https://youtu.be/TeALR63-LzE?si=O4b6DijZKrmR7teP)
> - Krita workflows are used for [Krita](https://krita.org/en/) + [Krita AI Diffusion](https://github.com/Acly/krita-ai-diffusion) + [Krita AI Tools](https://github.com/Acly/krita-ai-tools)
> - Sync version of Krita workflows can be opened by ComyUI and synchronized with Krita AI Diffusion.
> - Dev version of Krita workflows can only loaded by Krita AI Diffusion and should be moved to `...\AppData\Roaming\krita\ai_diffusion\workflows`.

## Required Custom Nodes

### Common & ComfyUI API

- (Common & API)[ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- (Common & API)[Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- (Common & API)[Inspire Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)
- (Common & API)[IP Adapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
- (Common & API)[KJ Nodes](https://github.com/kijai/ComfyUI-KJNodes)
- (Common & API)[Essentials](https://github.com/cubiq/ComfyUI_essentials)
- (Common & API)[ComfyUI ELLA](https://github.com/TencentQQGYLab/ComfyUI-ELLA)
- (Common & API)[Detail Daemon](https://github.com/Jonseed/ComfyUI-Detail-Daemon)
- (Common & API)[Seamless tiling](https://github.com/spinagon/ComfyUI-seamless-tiling)
- (Common & API)[JakeUpgrade](https://github.com/jakechai/ComfyUI-JakeUpgrade)
- (Common)[rgthree](https://github.com/rgthree/rgthree-comfy)
- (Common)[pythongosssss](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)
- (Common)[Ultimate SD Upscale](https://github.com/ssitu/ComfyUI_UltimateSDUpscale)
- (Common)[ComfyUI SAI API](https://github.com/Stability-AI/ComfyUI-SAI_API)

### imgen workflow
- (auto prompt)[Dynamic Prompts](https://github.com/adieyal/comfyui-dynamicprompts)
- (auto prompt)[One Button Prompt](https://github.com/AIrjen/OneButtonPrompt)
- (auto prompt)[Prompt Stylers](https://github.com/wolfden/ComfyUi_PromptStylers)
- (auto prompt)[Portrait Master](https://github.com/florestefano1975/comfyui-portrait-master)
- (auto prompt)[Flux Prompt Generator](https://github.com/fairy-root/Flux-Prompt-Generator)
- (auto prompt)[Merlin Magic Photo Prompter](https://github.com/Xclbr7/ComfyUI-Merlin)
- (auto prompt)[WD14 Tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger)
- (auto prompt)[VLM Nodes](https://github.com/gokayfem/ComfyUI_VLM_nodes)
- (auto prompt)[IF AI Tools](https://github.com/if-ai/ComfyUI-IF_AI_tools)
- (auto prompt)[Florence 2](https://github.com/kijai/ComfyUI-Florence2)
- (auto prompt)[ComfyUI Fal API](https://github.com/gokayfem/ComfyUI-fal-API)
- (refine)[Face Analysis](https://github.com/cubiq/ComfyUI_FaceAnalysis)
- (detailer)[Impact SubPack](https://github.com/ltdrdata/ComfyUI-Impact-Subpack)
- (detailer)[Segment Anything](https://github.com/storyicon/comfyui_segment_anything)
- (detailer)[Segment Anything 2](https://github.com/kijai/ComfyUI-segment-anything-2)
- (Seamless Texture)[Comfy mtb](https://github.com/melMass/comfy_mtb)
- (legacy)[NNLatentUpscale](https://github.com/Ttl/ComfyUi_NNLatentUpscale)
- (legacy)[ComfyUI Noise](https://github.com/BlenderNeko/ComfyUI_Noise)
- (legacy)[StyleAligned](https://github.com/brianfitzgerald/style_aligned_comfy)

### img2mesh workflow
- [ComfyUI 3D Pack](https://github.com/MrForExample/ComfyUI-3D-Pack)
- [ComfyUI Hunyuan3D Wrapper](https://github.com/kijai/ComfyUI-Hunyuan3DWrapper)
- [Comfy mtb](https://github.com/melMass/comfy_mtb)
- [ComfyUI-HQ-Image-Save](https://github.com/spacepxl/ComfyUI-HQ-Image-Save)
- (18 mv tex)[ComfyUI MVAdapter](https://github.com/huanngzh/ComfyUI-MVAdapter)
- (18 mv tex)[ComfyUI IG2MV](https://github.com/hunzmusic/ComfyUI-IG2MV)
- (18 mv tex)[ComfyUI StableX Wrapper](https://github.com/kijai/ComfyUI-StableXWrapper)

### video workflow
- [Wan Video Wrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)
- [AnimateDiff](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved)
- [Video Helper Suite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)
- [Frame Interpolation](https://github.com/Fannovel16/ComfyUI-Frame-Interpolation)
- [Florence 2](https://github.com/kijai/ComfyUI-Florence2)
- [Segment Anything 2](https://github.com/kijai/ComfyUI-segment-anything-2)
- [Mat Anyone](https://github.com/KytraScript/ComfyUI_MatAnyone_Kytra)
- (multi-gpu)[ComfyUI MultiGPU](https://github.com/pollockjj/ComfyUI-MultiGPU)

### Krita workflow
- [Inpaint Nodes](https://github.com/Acly/comfyui-inpaint-nodes)
- [Tooling Nodes](https://github.com/Acly/comfyui-tooling-nodes)

> [!NOTE]
> - [ComfyUI ELLA](https://github.com/TencentQQGYLab/ComfyUI-ELLA) is optional if you are not using SD15 workflow.
> - [ComfyUI SAI API](https://github.com/Stability-AI/ComfyUI-SAI_API) is for SAI API workflow.
> - [Comfy mtb](https://github.com/melMass/comfy_mtb): It is recommended to use `git clone` to install and block line 27 of `endpoint.py` to `# import_install("requirements")`, so the requirements will not be installed.

## JK_workflow : imgen (legacy)
<details>
<summary><b>Introduction</b></summary>

	Hotkey:
		0: usage guide
		\`: overall workflow
		1: base, image selection, & noise injection
		2: embedding, fine tune string, auto prompts, & adv conditioning parameters
		3: lora, controlnet parameters, & adv model parameters
		4: refine parameters
		5: detailer parameters
		6: upscale parameters
		7: In/Out Paint parameters

	Workflow Control:
		All switches in any Workflow panel take effect in realtime.
		All switches in any Select panel also affect sub workflow, but don't take effect in realtime, which needs preprocessing.
		All switches in Parameters panel that affect sub workflow don't take effect in realtime, which needs preprocessing.

	Suggested method:
		Preprocessing needs to be executed before actural generation for switches in Select or Parameters panels to control the sub workflow. 
		Pre-Queue Prompt: It's recommended to disable all processes in the Overall Workflow panel and adjust all sub-workflow-related switches before running Queue Prompt. The state of corresponding switches in Pre-process panels will be changed automatically after the preprocessing.
		Pre-process Pannel: Alternatively, you can preprocess manually by setting the corresponding switches in the Pre-process Pannel to the same state as in the Parameters Pannel, which does not need a Pre-Queue Prompt.

	Metadata:
		All parameters including sub-workflow-related switches will affect the generation result and also the content of Metadata saved with the image.
		In Refine image saving, remove noise_jinection_metadata link if not refining any noise injection process.
		In Upscale image saving, remove noise_jinection_metadata or refine_metadata link if not using Noise Injection or refine process.
		In Detailer image saving, remove noise_jinection_metadata, refine_metadata or upscale_metadata link if not using Noise Injection or refine process.

	SDXL switches:
		Image Resolution | AIO resolution
		Load SDXL Ckpt | Vae for Base | Refine | Upscale | Detailer | In/Out Paint
		FreeU SDXL settings
		Auto Variation SDXL settings
		Disable SD15 ELLA Text Encode (in Base Model Sub Workflow JK🐉)
		Enable SDXL Text Ecode (in Base Model Sub Workflow JK🐉) (Optional)
		Enable SDXL Dual Clip (in Base Model Sub Workflow JK🐉) (Optional)
		Enable SDXL Refine Text Encode (in Refine Sub Workflow JK🐉) (optional)
		Switch plus, plus-face, and faceid ipadapter to sdxl_vit-h version
		Switch faceid lora to sdxl version
		Switch Image Upscale ControlNet Depth|Tile to sdxl version (in Upscale Sub Workflow JK🐉)
		Switch NNLatentUpscale version to SDXL
		Set Ultimate SD Upscale Tile size to 1024
		Switch Detailer's Add Detail Lora to SDXL version
		Switch Hand Fix Depth ControlNet version to SDXL
		Hand Fix MeshGraphhormer Hand Refiner resolution
		Use Load ControNet Model and set Union ControlNet type to load xinsir controlnet union in I/O Paint process
		Enable Black Pixel switch for Inpaint/Outpaint ControlNet in I/O Paint process
		(If it is SD15, choose the opposite)

	Other:
		1. Nodes State JK🐉 uses target nodes' id to control their active | mute | bypass mode. Need to update node_id_list if you make a copy.
		2. The order of Detailer Progress and Upscale Progress can be swapped. Please avoid to form loops. 
</details>

<details>
<summary><b>Explanation</b></summary>

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/0-1_OverallWorkflow.png)
- Overall Workflow

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/0-2_ImageComparer.png)
- Image Comparer

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-1_ProjectSetting.png)
- Project Setting

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-2_BaseCkptVaeSeed.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-3_BaseModelParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-4_BaseModelSubWorkflowNNoiseInjectionParameter.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-5_ImageInputSelect.png)
- Base Model Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-1_TI.png)
- TI Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-2_FineTuneString.png)
- Fine Tune String Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-3_AutoVariationPrompt.png)
- Auto Variation Prompt Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-4_AdvancedConditioning.png)
- Advanced Conditioning Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/3-1_Lora.png)
- Lora Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/3-2_ControlNet.png)
- Control Net Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/3-3_AdvancedModel.png)
- Advanced Model Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/4-1_RefineProcessCkptSeed.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/4-2_RefineModelParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/4-3_RefineSubProcessWorkflow.png)
- Refine Process Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-1_UpscaleProcess.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-2_UpscaleCkptSeed.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-3_UpscaleParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-4_UpscaleSubWorkflow.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-5_UpscaleNoiseInjection.png)
- Upscale Process Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/6-1_DetailerProcessSelect.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/6-2_DetailerParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/6-3_DetailerSubWorkflow.png)
- Detailer Process Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/7-1_InOutPaintProcessSelect.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/7-2_InOutPaintCkptVae.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/7-3_InOutPaintSubWorkflow.png)
- In/Out Paint Process Parameters
</details>

## JK_workflow : img2mesh
<details>
<summary><b>Introduction</b></summary>

	Hotkey:
		\`: Main Workflow Control Pannels
	
	Workflow Control:
		Each img2mesh workflow contains several sub-workflows as the filename indicates.
		Each sub-workflow consists of one or more sub-steps.
		Each sub-step saves the result as images or meshes when it finishes generation.
		Each sub-step can switch from generation mode to loading mode.
		It's recommended to enable sub-step step by step and switch to loading mode after the generation.
	
	Other:
		TripoSR workflow is not included because it is straightforward.
		Triplane workflow is not included because it is straightforward.
</details>

<details>
<summary><b>Explanation</b></summary>

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh-types.png)
- Workflow breakdown: img2mesh types

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_CRM&Zero123plus&MVDream&CharacterGen-structure.png)
- Workflow breakdown: CRM&Zero123plus&MVDream&CharacterGen

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Unique3D&Wonder3D&Era3D-structure.png)
- Workflow breakdown: JUnique3D&Wonder3D&Era3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Zero123&SV3D-structure.png)
- Workflow breakdown: Zero123&SV3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_3DGS-structure.png)
- Workflow breakdown: 3DGS

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_CRM&Zero123plus&MVDream&CharacterGen.png)
- Workflow Control Panels: CRM&Zero123plus&MVDream&CharacterGen

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Unique3D&Wonder3D&Era3D.png)
- Workflow Control Panels: Unique3D&Wonder3D&Era3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Zero123&SV3D.png)
- Workflow Control Panels: Zero123&SV3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_3DGS.png)
- Workflow Control Panels: 3DGS
</details>

## JakeUpgrade Nodes
<details>
<summary><b>Custom Nodes</b></summary>

	Misc Nodes
		SD1.5 Aspect Ratio JK🐉
		SDXL Aspect Ratio JK🐉
		SD3 Aspect Ratio JK🐉
		Aspect Ratio JK🐉
		Tiling Mode JK🐉
		Empty Latent Color JK🐉
		Random Beats JK🐉
		SDXL Target Res JK🐉
		Get Size JK🐉
		Image Crop by Mask Resolution JK🐉
		Image Crop by Mask Params JK🐉,
		Latent Crop Offset JK🐉
		Scale To Resolution JK🐉
		Inject Noise Params JK🐉
		SD3 Prompts Switch JK🐉
		Save String List To JSON JK🐉
		Load String List From JSON JK🐉
    Reroute Nodes
		Reroute List JK🐉
		Reroute Ckpt JK🐉
		Reroute Vae JK🐉
		Reroute Sampler JK🐉
		Reroute Upscale JK🐉
		Reroute Resize JK🐉
		Reroute String JK🐉
		String To Combo JK🐉
    ControlNet Nodes
		Apply ControlNet JK🐉
		Multi-ControlNet Stack JK🐉
		ControlNet Loader JK🐉
		Multi-ControlNet Param Stack JK🐉
		Apply Multi-ControlNet JK🐉
		Apply Multi-ControlNet Adv JK🐉
    LoRA Nodes
		Load LoRA JK🐉
		LoRA Stack JK🐉
		Apply LoRA Stack JK🐉
    Embedding Nodes
		Embedding Picker JK🐉
		Embedding Picker Multi JK🐉
    Loader Nodes
		Ckpt Loader JK🐉
		Vae Loader JK🐉
		Sampler Loader JK🐉
		Upscale Model Loader JK🐉
    Pipe Nodes
		Nodes State JK🐉
		Ksampler Parameters JK🐉
		Ksampler Parameters Default JK🐉
		Guidance Default JK🐉
		Project Setting JK🐉
		Base Model Parameters JK🐉
		Base Model Parameters Extract JK🐉
		Base Image Parameters Extract JK🐉
		Base Model Pipe JK🐉
		Base Model Pipe Extract JK🐉
		Base Model Parameters SD3 JK🐉
		Refine Pipe JK🐉
		Refine Pipe Extract JK🐉
		Noise Injection Parameters JK🐉
		Noise Injection Pipe Extract JK🐉
		Refine Model Parameters JK🐉
		Refine 1 Parameters Extract JK🐉
		Refine 2 Parameters Extract JK🐉
		Upscale Model Parameters JK🐉
		Image Upscale Parameters Extract JK🐉
		Latent Upscale Parameters Extract JK🐉
		Upscale Model Parameters Extract JK🐉
		Detailer Parameters JK🐉
		Pipe End JK🐉
		Metadata Pipe JK🐉
		Metadata Pipe Extract JK🐉
    Image Nodes
		Save Image With Metadata JK🐉
		Save Image With Metadata Flow JK🐉
		Load Image With Metadata JK🐉
		Load Image With Alpha JK🐉
		Make Image Grid JK🐉
		Split Image Grid JK🐉
		Enchance And Resize Hint Images JK🐉
		Image Resize Mode JK🐉
		Remove Image Alpha JK🐉
		Color Grading JK🐉
		Rough Outline JK🐉
		Open+DW Pose JK🐉
	Mask Nodes
		Is Mask Empty JK🐉
    Animation Nodes
		Animation Prompt JK🐉
		Animation Value JK🐉
    Logic switches Nodes
		Boolean JK🐉
		Image Input Switch JK🐉
		Mask Input Switch JK🐉
		Int Input Switch JK🐉
		Float Input Switch JK🐉
		Latent Input Switch JK🐉
		Conditioning Input Switch JK🐉
		Clip Input Switch JK🐉
		Model Input Switch JK🐉
		ControlNet Input Switch JK🐉
		ControlNet Stack Input Switch JK🐉
		Text Input Switch JK🐉
		VAE Input Switch JK🐉
		Pipe Input Switch JK🐉
		Impact Pipe Input Switch JK🐉
		Noise Input Switch JK🐉
		Guider Input Switch JK🐉
		Sampler Input Switch JK🐉
		Sigmas Input Switch JK🐉
		Mesh Input Switch JK🐉
		Ply Input Switch JK🐉
		Orbit Pose Input Switch JK🐉
		TriMesh Input Switch JK🐉
    ComfyMath Fix Nodes
		BoolToInt JK🐉
		IntToBool JK🐉
		BoolUnaryOp JK🐉
		BoolBinaryOp JK🐉
		Bool And JK🐉
		Bool OR JK🐉
		StringBinaryCon JK🐉
		Prompt Combine JK🐉
		FloatUnaryCon JK🐉
		FloatBinaryCon JK🐉
		IntUnaryCon JK🐉
		IntBinaryCon JK🐉
		NumberUnaryCon JK🐉
		NumberBinaryCon JK🐉
		Vec2UnaryCon JK🐉
		Vec2BinaryCon JK🐉
		Vec2ToFloatUnaryOp JK🐉
		Vec2ToFloatBinaryOp JK🐉
		Vec2FloatOp JK🐉
		Vec3UnaryCon JK🐉
		Vec3BinaryCon JK🐉
		Vec3ToFloatUnaryOp JK🐉
		Vec3ToFloatBinaryOp JK🐉
		Vec3FloatOp JK🐉
		Vec4UnaryCon JK🐉
		Vec4BinaryCon JK🐉
		Vec4ToFloatUnaryOp JK🐉
		Vec4ToFloatBinaryOp JK🐉
		Vec4FloatOp JK🐉
    ComfyMath Nodes
		FloatToInt JK🐉
		IntToFloat JK🐉
		IntToNumber JK🐉
		NumberToInt JK🐉
		FloatToNumber JK🐉
		NumberToFloat JK🐉
		ComposeVec2 JK🐉
		ComposeVec3 JK🐉
		ComposeVec4 JK🐉
		BreakoutVec2 JK🐉
		BreakoutVec3 JK🐉
		BreakoutVec4 JK🐉
		FloatUnaryOp JK🐉
		FloatBinaryOp JK🐉
		IntUnaryOp JK🐉
		IntBinaryOp JK🐉
		NumberUnaryOp JK🐉
		NumberBinaryOp JK🐉
		Vec2UnaryOp JK🐉
		Vec2BinaryOp JK🐉
		Vec3UnaryOp JK🐉
		Vec3BinaryOp JK🐉
		Vec4UnaryOp JK🐉
		Vec4BinaryOp JK🐉
    Simple Evaluate Nodes
		Evaluate Ints JK🐉
		Evaluate Floats JK🐉
		Evaluate String JK🐉
    	Evaluate Examples JK🐉
	3D Nodes
		Orbit Poses JK🐉
		OrbitLists to OrbitPoses JK🐉
		OrbitPoses to OrbitLists JK🐉
		Get OrbitPoses From List JK🐉
</details>

<details>
<summary><b>Group Nodes</b></summary>

	Tools
		JK🐉::Image Crop by Mask
		JK🐉::Image Crop by Mask and Resize
		JK🐉::Image Crop by Mask and Resize (Input)
		JK🐉::Image RemBG
		JK🐉::Image Resize
		JK🐉::Image Stitch by Mask
		JK🐉::Latent Crop by Mask
		JK🐉::Latent Crop by Mask and Resize
		JK🐉::Latent Crop by Mask and Resize (Input)
		JK🐉::Latent Resize
		JK🐉::Latent Stitch by Mask
	Workflow
		JK🐉::Concept
		JK🐉::Flux KSampler
		JK🐉::Flux KSampler Adv
		JK🐉::Variation Ksampler
		JK🐉::Image Gen Common
		JK🐉::Image Gen Common (Input)
		JK🐉::Image Gen Common (Pipe)
		JK🐉::Image Gen Common Adv
		JK🐉::Image Gen Common Adv (Input)
		JK🐉::Image Gen Common Adv (Pipe)
		JK🐉::Image Gen Flux
		JK🐉::Image Gen Flux (Input)
		JK🐉::Image Gen Flux (Pipe)
		JK🐉::Image Gen Flux Adv
		JK🐉::Image Gen Flux Adv (Input)
		JK🐉::Image Gen Flux Adv (Pipe)
		JK🐉::Image Gen SD15
		JK🐉::Image Gen SD15 (Input)
		JK🐉::Image Gen SD15 (Pipe)
		JK🐉::Image Gen SD15 Adv
		JK🐉::Image Gen SD15 Adv (Input)
		JK🐉::Image Gen SD15 Adv (Pipe)
		JK🐉::Image Gen SD3
		JK🐉::Image Gen SD3 (Input)
		JK🐉::Image Gen SD3 (Pipe)
		JK🐉::Image Gen SD3 Adv
		JK🐉::Image Gen SD3 Adv (Input)
		JK🐉::Image Gen SD3 Adv (Pipe)
		JK🐉::Image Gen SDXL
		JK🐉::Image Gen SDXL (Input)
		JK🐉::Image Gen SDXL (Pipe)
		JK🐉::Image Gen SDXL Adv
		JK🐉::Image Gen SDXL Adv (Input)
		JK🐉::Image Gen SDXL Adv (Pipe)
		JK🐉::Image Refine Common
		JK🐉::Image Refine Common (Input)
		JK🐉::Inpaint Latent
		JK🐉::Inpaint Checkpoint
		JK🐉::Inpaint ControlNet			
		JK🐉::Outpaint Latent
		JK🐉::Outpaint Checkpoint
		JK🐉::Outpaint ControlNet
</details>

## Reference Custom Nodes
- [rgthree](https://github.com/rgthree/rgthree-comfy)
- [Comfyroll](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes)
- [Efficiency Nodes](https://github.com/jags111/efficiency-nodes-comfyui)
- [ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [Image Saver](https://github.com/giriss/comfy-image-saver)
- [Prompt Reader](https://github.com/receyuki/comfyui-prompt-reader-node)
- [ComfyMath](https://github.com/evanspearman/ComfyMath)
- [Embedding Picker](https://github.com/Tropfchen/ComfyUI-Embedding_Picker)
- [Layer Style](https://github.com/chflame163/ComfyUI_LayerStyle)
