/**
 * Advanced 3D Viewer,
 * supports GLB, FBX, SMPL bin, OBJ, and PLY formats
 * with/without camera animation
 * and with custom camera animation
 * and exported as GLB
 */
import { app } from "../../scripts/app.js";

const ADV3DVIEWER_HTML = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
	<style>
		/* CSS变量集中管理*/
		:root {
			--primary-color: #4a9eff;
			--danger-color: #ff4444;
			--bg-dark: #1a1a1a;
			--bg-panel: #252525;
			--bg-input: #333;
			--border-color: #555;
			--text-primary: #ccc;
			--text-secondary: #aaa;
			--text-muted: #666;
		}
		
		/* 基础重置*/
		html, body { 
			width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden; 
			background: var(--bg-dark); font-family: Arial, sans-serif; 
		}
		
		#container { 
			display: flex; flex-direction: column; width: 100%; height: 100%; 
		}
		
		#canvas-container { 
			flex: 1; position: relative; overflow: hidden; width: 100%; 
			min-height: 0; background: #000; 
		}
		
		/* 控制面板*/
		#controls {
			min-height: 89px;
			flex-shrink: 0;
			background: var(--bg-panel);
			display: flex;
			flex-direction: column;
			padding: 5px 8px;
			gap: 4px;
			border-top: 1px solid #333;
			z-index: 200;
			overflow-x: auto;
			scrollbar-width: none;
			-ms-overflow-style: none;
			cursor: grab;
		}
		#controls::-webkit-scrollbar { display: none; }
		#controls.grabbing { cursor: grabbing; }
		
		/* 控制行*/
		.control-row {
			display: flex;
			align-items: center;
			height: 26px;
			flex-shrink: 0;
			width: 875px;
			gap: 6px;
		}
		
		/* 控制组*/
		.control-group {
			display: flex;
			align-items: center;
			gap: 3px;
			flex-shrink: 0;
		}
		
		.separator {
			color: var(--text-muted);
			font-size: 10px;
			width: 8px;
			text-align: center;
			flex-shrink: 0;
		}
		
		#info-display {
			position: absolute;
			top: 8px;
			right: 8px;
			color: rgba(255, 255, 255, 0.7);
			font-size: 11px;
			pointer-events: none;
			background: rgba(0,0,0,0.5);
			padding: 3px 6px;
			border-radius: 3px;
			z-index: 10;
			font-family: monospace;
		}
		
		#loading {
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			color: white;
			font-size: 14px;
			background: rgba(0,0,0,0.8);
			padding: 12px 16px;
			border-radius: 6px;
			z-index: 100;
			display: none;
		}
		
		.disabled-control {
			opacity: 0.4 !important;
			cursor: not-allowed !important;
			pointer-events: none;
		}
		
		.enabled-control {
			opacity: 1 !important;
			pointer-events: auto;
		}
		
		/* 按钮基础样式*/
		button {
			background: var(--primary-color);
			border: none;
			color: white;
			border-radius: 3px;
			width: 24px;
			height: 24px;
			cursor: pointer;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 12px;
			flex-shrink: 0;
		}
		button:hover:not(.disabled-control) { 
			background: #3a8eef; 
		}
		button:disabled { 
			background: #444; 
			cursor: default; 
			opacity: 0.4; 
		}
		/* 特殊按钮*/
		.clear-btn { background: var(--danger-color); }
		.clear-btn:hover { background: #cc3333; }
		.record-btn { background: var(--primary-color); }
		.record-btn:hover { background: #3a8eef; }
		.recording { 
			background: var(--danger-color);
			animation: pulse 1s infinite;
		}
		
		/* 滑块基础样式*/
		input[type=range] {
			height: 3px;
			background: #444;
			border-radius: 2px;
			outline: none;
			flex-shrink: 0;
		}
		input[type=range]::-webkit-slider-thumb {
			-webkit-appearance: none;
			width: 12px;
			height: 12px;
			border-radius: 50%;
			background: var(--primary-color);
			cursor: pointer;
		}
		input[type=range]::-moz-range-thumb {
			width: 12px;
			height: 12px;
			border-radius: 50%;
			background: var(--primary-color);
			cursor: pointer;
			border: none;
		}
		/* 滑块分类宽度*/
		.light-slider { width: 48px; }
		.time-slider { width: 187px; }
		.helper-size-slider { width: 59px; }
		
		/* 输入框样式*/
		input[type=color] { 
			width: 24px; height: 24px; border: none; 
			border-radius: 3px; cursor: pointer; 
			background: transparent; flex-shrink: 0; 
		}
		
		input[type=checkbox] { 
			width: 14px; height: 14px; cursor: pointer; 
			flex-shrink: 0; 
		}
		
		input[type="number"].pending {
			border-color: var(--primary-color) !important;
			box-shadow: 0 0 3px rgba(74, 158, 255, 0.5);
		}
		input[type=number] {
			width: 45px; height: 20px;
			background: var(--bg-input);
			border: 1px solid var(--border-color);
			border-radius: 2px;
			color: white;
			padding: 0 4px;
			font-size: 11px;
			flex-shrink: 0;
		}
		/* 数字输入框验证失败状态 */
		input[type="number"].invalid {
			border-color: var(--danger-color) !important;
			box-shadow: 0 0 3px rgba(255, 68, 68, 0.5);
		}
		
		/* 文本标签样式*/
		.control-label {
			color: var(--text-secondary);
			font-size: 11px;
			min-width: 24px;
			flex-shrink: 0;
			text-align: left;
		}
		.control-label#fov-label {
			min-width: 30px;
			display: inline-block;
		}
		.frame-counter {
			color: var(--text-secondary);
			font-family: monospace;
			font-size: 11px;
			width: 70px;
			text-align: right;
			flex-shrink: 0;
		}
		.keyframe-count { 
			color: var(--text-secondary);
			font-size: 10px;
			width: 29px; 
			text-align: right; 
			flex-shrink: 0;
		}
		/* 特定标签宽度*/
		.fixed-width-label-light { width: 64px; }
		.fixed-width-label-shadow { width: 37px; }
		.fixed-width-label-ortho { width: 27px; }
		.fixed-width-label-clip { width: 59px; }
		.fixed-width-label-roll { width: 24px; }
		.fixed-width-label-helper-size { width: 57px; }
		.fixed-width-label-mat { width: 45px; }
		.fixed-width-label-bg-color { width: 46px; }
		.fixed-width-label-side { width: 24px; }
		
		/* Views下拉菜单 */
		#views-select {
			width: 105px;
			height: 20px;
			background: var(--bg-input);
			border: 1px solid var(--border-color);
			border-radius: 2px;
			color: white;
			padding: 0 4px;
			font-size: 11px;
			flex-shrink: 0;
		}
		#material-mode-select {
			width: 85px;
			height: 20px;
			background: var(--bg-input);
			border: 1px solid var(--border-color);
			border-radius: 2px;
			color: white;
			padding: 0 4px;
			font-size: 11px;
			flex-shrink: 0;
		}
		#side-select {
			width: 66px;
			height: 20px;
			background: var(--bg-input);
			border: 1px solid var(--border-color);
			border-radius: 2px;
			color: white;
			padding: 0 4px;
			font-size: 11px;
			flex-shrink: 0;
			margin-left: 2px;
		}
		
		#delete-custom-camera:hover {
			background: #cc3333;
		}
		
		/* 隐藏文件输入*/
		.hidden-file-input { display: none; }
		
		/* 动画*/
		@keyframes pulse {
			0% { background-color: #ff4444; }
			50% { background-color: #ff8888; }
			100% { background-color: #ff4444; }
		}
		
		/* 灯光GUI容器样式 */
		.light-gui-container {
			position: absolute;
			bottom: 8px;
			left: 8px;
			z-index: 1001;
			background: rgba(30, 30, 30, 0.9);
			border: 1px solid #444;
			border-radius: 3px;
			padding: 4px;
			width: 180px;
			max-height: 524px;
			overflow-y: auto;
			backdrop-filter: blur(5px);
		}
		
		/* 后处理GUI容器样式 */
		.material-gui-container {
			position: absolute;
			bottom: 8px;
			right: 8px;
			z-index: 1000;
			background: rgba(30, 30, 30, 0.9);
			border: 1px solid #444;
			border-radius: 3px;
			padding: 4px;
			width: 180px;
			max-height: 300px;
			overflow-y: auto;
			backdrop-filter: blur(5px);
		}
		
	</style>
</head>
<body>
    <div id="container">
        <div id="canvas-container">
            <div id="loading">Waiting for 3D data...</div>
            <div id="info-display">960x540 | Model Format: None</div>
        </div>
        <div id="controls">
            <!-- 第一行 -->
            <div class="control-row">
                <!-- 文件管理组 -->
                <div class="control-group">
                    <button id="import-btn" class="file-btn" title="Import Model">📥</button>
					<button id="export-btn" class="file-btn" title="Save GLB">💾</button>
                    <button id="diagnostic-btn" title="Run Diagnostics in Console">🔍</button>
					<button id="clear-btn" class="file-btn" title="Clear Scene">❌</button>
                </div>
                <div class="separator">|</div>
                
                <!-- 信息组 -->
                <div class="control-group">
                    <label class="control-label">Info Tag</label>
                    <input type="checkbox" id="info-display-toggle" checked title="Toggle Info Display">
                </div>
                <div class="separator">|</div>
                
                <!-- 辅助组 -->
                <div class="control-group">
                    <label class="control-label">Helper</label>
                    <input type="checkbox" id="helper-toggle" checked title="Toggle Grid and Axes">
                </div>
                <div class="separator">|</div>
                
                <!-- 材质组 -->
				<div class="control-group">
					<label class="control-label fixed-width-label-mat" id="mat-mode-label" >Material</label>
					<select id="material-mode-select" title="Material Mode">
						<option value="original">Original</option>
						<option value="default">Default</option>
						<option value="wireframe">Wireframe</option>
						<option value="normal">Normal</option>
						<option value="depth">Depth</option>
						<option value="lineart">Lineart</option>
						<option value="canny">Canny</option>
						<option value="edge">Edge</option>
						<option value="contour">Contour</option>
						<option value="ssao">SSAO</option>
						<option value="gtao">GTAO</option>
					</select>
				</div>
                <div class="separator">|</div>
				
				<div class="control-group">
					<label class="control-label fixed-width-label-bg-color" id="bg-color-label">BG Color</label>
					<input type="color" id="bg-color-picker" title="Background Color">
					<label class="control-label fixed-width-label-side" id="side-label">Side</label>
					<select id="side-select" title="Rendering Side">
						<option value="Front">Front</option>
						<option value="Back">Back</option>
						<option value="Double">Double</option>
					</select>
				</div>
                <div class="separator">|</div>
                
                <!-- 灯光组 -->
				<div class="control-group">
					<label class="control-label fixed-width-label-light" id="light-mode-label">Default Light</label>
					<input type="checkbox" id="light-mode-toggle" title="Toggle between default light and scene light">
                    <label class="control-label fixed-width-label-shadow" id="shadow-mode-label">Shadow</label>
                    <input type="checkbox" id="shadows-toggle" checked title="Enable Soft Shadow">
                    <button id="reset-settings" class="compact-btn" title="Reset Settings">🔄</button>
                </div>
				<div class="separator">|</div>
				
                <!-- 高级设置 -->
                <div class="control-group">
					<label class="control-label fixed-width-label-helper-size">Helper Size</label>
					<input type="range" id="helper-size-slider" class="helper-size-slider" min="0.1" max="5" step="0.1" value="1.0" title="Helper Visualization Size">
	                </div>
            </div>
			
            <!-- 第二行 -->
            <div class="control-row">
                <!-- 播放控制组 -->
			<div class="control-group">
					<button id="first-frame" title="First Frame">⏮️</button>
					<button id="prev-keyframe" title="Previous Custom Camera Keyframe">⏪</button>
					<button id="prev-frame" title="Previous Frame">⏫</button>
					<button id="reverse-play" title="Reverse Play">◀️</button>
					<button id="play-btn" title="Play">▶️</button>
					<button id="next-frame" title="Next Frame">⏬</button>
					<button id="next-keyframe" title="Next Custom Camera Keyframe">⏩</button>
					<button id="last-frame" title="Last Frame">⏭️</button>
					<button id="toggle-camera-anim" title="Switch to Play Mode">🎥</button>
					<input type="number" id="fps-input" min="1" max="120" value="30" title="Frames Per Second" style="width: 45px;">
					<button id="record-btn" class="file-btn record-btn" title="Record Video">🎬</button>
				</div>
				<div class="separator">|</div>
                
                <!-- 时间线组 -->
				<div class="control-group">
					<input type="range" id="slider" class="time-slider" min="0" max="149" value="0" step="1" title="Timeline Slider">
					<div class="frame-counter" id="frame-display">0 / 149</div>
				</div>
				<div class="separator">|</div>
                
                <!-- 帧数设置组 -->
				<div class="control-group">
					<input type="number" id="start-frame" min="-1000" value="0" title="Start Frame" style="width: 60px;">
					<span style="color: #ccc; font-size: 10px; width: 8px; text-align: center;">-</span>
					<input type="number" id="end-frame" min="0" value="149" title="End Frame" style="width: 60px;">
					<button id="scene-length-btn" class="compact-btn" title="Set to Scene Length">📏</button>
				</div>
				<div class="separator">|</div>
				
				<!-- 高级设置 -->
				<div class="control-group">
				
				</div>
            </div>
			
            <!-- 第三行 -->
            <div class="control-row">
                <!-- 视窗组 -->
                <div class="control-group">
					<select id="views-select" title="Views">
						<option value="User">User</option>
						<option value="Front">Front</option>
						<option value="Back">Back</option>
						<option value="Left">Left</option>
						<option value="Right">Right</option>
						<option value="Top">Top</option>
						<option value="Bottom">Bottom</option>
					</select>
                    <button id="new-camera-btn" class="compact-btn" title="New Camera">📷</button>
					<button id="center-to-object-btn" title="Move Camera to Scene Center">👁️</button>
					<button id="focus-to-object-btn" title="Set Near and Far Clip Plane to Scene Depth">📐</button>
                </div>
                <div class="separator">|</div>
                
                <!-- 相机动画组 -->
                <div class="control-group">
                    <button id="auto-keyframe" title="Auto Add Camera Keyframe">🔘</button>
					<button id="add-keyframe" title="Add Camera Keyframe">➕</button>
                    <button id="delete-keyframe" title="Delete Current Keyframe">➖</button>
                    <button id="clear-keyframes" title="Clear All Keyframes">🗑️</button>
                    <button id="delete-custom-camera" class="file-btn" title="Delete Current Custom Camera">❌</button>
                    <span id="keyframe-count" class="keyframe-count">0 🔑</span>
                </div>
                <div class="separator">|</div>
                
                <!-- 相机控制组 -->
				<div class="control-group">
					<label class="control-label fixed-width-label-ortho">Ortho</label>
					<input type="checkbox" id="orthographic-toggle" title="Orthographic Projection">
					<label class="control-label" id="fov-label">FOV</label>
					<input type="number" id="fov-input" min="0.0" max="180.0" step="0.01" value="50" title="Field of View / View Size" style="width: 60px;">
				</div>
				<div class="separator">|</div>
				
				<div class="control-group">
					<label class="control-label fixed-width-label-clip">Clip Plane</label>
					<input type="number" id="near-input" min="0.01" max="5000" step="0.01" value="0.01" title="Near Clipping Plane" style="width: 60px;">
					<span style="color: #ccc; font-size: 10px; width: 8px; text-align: center;">-</span>
					<input type="number" id="far-input" min="0.02" max="5000" step="0.01" value="500.00" title="Far Clipping Plane" style="width: 60px;">
					<button id="reset-camera" class="compact-btn" title="Reset Camera">🔄</button>
				</div>
				<div class="separator">|</div>
				
				<!-- 高级设置 -->
				<div class="control-group">
					<label class="control-label fixed-width-label-roll">Roll</label>
					<input type="number" id="roll-angle" min="-180.0" max="180.0" step="0.01" value="0.00" title="Roll Angle" style="width: 60px;">
					<button id="y-up-btn" title="Set Up Vector to +Y">⬆</button>
				</div>
            </div>
        </div>
    </div>
	
    <input type="file" id="import-file-input" class="hidden-file-input" accept=".glb,.fbx,.bin,.obj,.ply">
	
    <script type="importmap">
    {
        "imports": {
            "three": "https://cdn.jsdelivr.net/npm/three@0.162.0/build/three.module.js",
			"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/"
        }
    }
    </script>
	
    <script type="module">
		import * as THREE from 'three';
		import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
		import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
		import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
		import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
		import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
		import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';
		import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
		import { TextureLoader } from 'three';
		import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
		import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
		import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
		import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
		import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
		
        class Adv3DViewer {
			// 初始化
			constructor() {
				this.dom = this.cacheDOM();
				this.state = {
					currentModel: null,
					currentFormat: null,
					currentAnimations: [],
					currentMixer: null,
					currentFileData: null,
					smplData: null,
					smplMesh: null,
					
					grid: null,
					axesHelper: null,
					loading: false,
					helperSize: 1.0, 
					defaultSettings: {
						startFrame: 0,
						endFrame: 149,
						dirLight: 1.5,
						ambLight: 0.6,
						meshColor: '#4a9eff',
						bgColor: '#111111'
					},
					
					sceneBBox: null,
					sceneCenter: new THREE.Vector3(),
					animationBBoxData: {
						sampledFrames: new Map(),
						aggregated: {
							overallMin: null,
							overallMax: null,
							averageCenter: null,
							overallSize: null
						},
						cachedFrames: new Map(),
						sampleFrameNumbers: [],
						samplingInterval: 25,
						isInitialized: false,
						hasAnimation: false
					},
					
					useSceneLight: false,
					lights: {
						dir: null,
						amb: null,
						default: [],
						scene: [],
						
						dirColor: '#ffffff',
						dirIntensity: 2.5,
						dirSpherical: {
							radius: 5,
							azimuth: 45,
							elevation: 45
						},
						
						shadowsEnabled: false,
						shadowSettings: {
							shadowType: 'pcfsoft',
							shadowTypes: {
								'basic': THREE.BasicShadowMap,
								'pcf': THREE.PCFShadowMap,
								'pcfsoft': THREE.PCFSoftShadowMap,
								'vsm': THREE.VSMShadowMap
							},
							mapSize: 2048,
							radius: 4,
							samples: 8,
							bias: -0.0001,
							normalBias: 0.01,
							camera: {
								near: 0.1,
								far: 10,
								left: -5,
								right: 5,
								top: 5,
								bottom: -5
							}
						},
						
						ambColor: '#ffffff',
						ambIntensity: 0.6
					},
					
					cameras: {
						activeScene: null,
						default: [],
						custom: [],
						scene: [],
						customCount: 0,
						states: new Map(),
						currentType: 'default'
					},
					controlTargetDist: {
						minDist: 0.01,
						maxDist: 10000,
						defDist: 5
					},
					cameraAnim: {
						isEnabled: false,
						originalControlsEnabled: true
					},
					autoAddKeyframeEnabled: false,
					
					materialMode: 'original',
					originalMaterials: new Map(),
					materials: {
						default: null,
						normal: null,
						depth: null,
						wireframe: null,
						lineart: null,
						contour: null,
						edge: null,
						canny: null
					},
					materialParams: {
						default: {
							color: '#4a9eff',
							roughness: 1.0,
							metalness: 0.0,
							flatShading: false
						},
						wireframe: {
							color: '#888888',
							linewidth: 1,
							opacity: 1.0
						},
						normal: {
							flatShading: false
						},
						lineart: {
							color: '#ffffff',
							edgeStart: 0.6,
							edgeEnd: 0.9,
							curvatureStart: 0.01,
							curvatureEnd: 0.05
						},
						edge: {
							color: '#ffffff',
							normalThreshold: 1.0,
							posThreshold: 1.0,
							edgeStart: 0.1, 
							edgeEnd: 0.2,
							contrast: 2.0
						},
						canny: {
							color: '#ffffff',
							lowThreshold: 0.1,
							highThreshold: 0.3,
							edgeStrength: 1.0,
							edgeDetail: 0.1
						},
						contour: {
							color: '#ffffff',
							thickness: 1.5,
							depthThreshold: 0.015,
							normalThreshold: 0.4
						}
					},
					postProcessingParams: {
						ssao: {
							kernelRadius: 16,
							minDistance: 0.001,
							maxDistance: 0.05,
							output: SSAOPass.OUTPUT.Blur
						},
						gtao: {
							radius: 0.25,
							distanceExponent: 1.0,
							thickness: 1.0,
							scale: 1.0,
							distanceFallOff: 1.0,
							samples: 16,
							output: GTAOPass.OUTPUT.Denoise
						}
					},
					commonParams: {
						side: 'Front',
						background: '#111111'
					},
					
					textureLoader: null,
					useVertexColors: false,
					textureMapping: true,
					originalTextures: new Map(),
					textureCache: new Map(),
					
					playback: {
						isPlaying: false,
						isReversed: false,
						currentFrame: 0,
						totalFrames: 0,
						fps: 30,
						startFrame: 0,
						endFrame: 149,
						clock: new THREE.Clock()
					},
					
					recording: {
						isRecording: false,
						mediaRecorder: null,
						chunks: [],
						originalGridVisible: true,
						originalInfoVisible: true
					},
					
					materialGUI: {
						visible: false,
						guiInstance: null,
						container: null,
						commonFolder: null,
						defaultFolder: null,
						normalFolder: null,
						wireframeFolder: null,
						lineartFolder: null,
						edgeFolder: null,
						cannyFolder: null,
						contourFolder: null,
						ssaoFolder: null,
						gtaoFolder: null
					},
					lightGUI: {
						visible: false,
						guiInstance: null,
						container: null,
						dirLightFolder: null,
						ambLightFolder: null
					}
				};
				
				this.fps = {
					value: 0,
					frameCount: 0,
					lastTime: performance.now(),
					updateInterval: 1000,
					lastUpdateTime: 0
				};
				
				this._messageTimer = null;
				this.renderer = null;
				this.composer = null;
				this.contourPass = null;
				this.normalRenderTarget = null;
				this.depthTexture = null;
				this.isContourMode = false;
				
				this.camera = null;
				this.controls = null;
				
				this.scene = null;
				this.loaders = {
					gltf: new GLTFLoader(),
					fbx: new FBXLoader(),
					obj: new OBJLoader(),
					ply: new PLYLoader()
				};
				
				this.exporter = new GLTFExporter();
				
				this.init();
			}

			cacheDOM() {
				const get = (id) => document.getElementById(id);
				return {
					container: get('canvas-container'), controlsPanel: get('controls'), loading: get('loading'), infoDisplay: get('info-display'),
					labels: {
						keyCount: get('keyframe-count'),
						matLabel: get('material-mode-label'),
						bgColorLabel: get('bg-color-label'),
						lightLabel: get('light-mode-label'),
						ortho: document.querySelector('.fixed-width-label-ortho'),
						clip: document.querySelector('.fixed-width-label-clip'),
						roll: document.querySelector('.fixed-width-label-roll'),
						fov: get('fov-label')
					},
					btns: {
						play: get('play-btn'),
						reverse: get('reverse-play'),
						first: get('first-frame'),
						last: get('last-frame'),
						prevKey: get('prev-keyframe'),
						nextKey: get('next-keyframe'),
						prevFrame: get('prev-frame'),
						nextFrame: get('next-frame'),
						import: get('import-btn'),
						export: get('export-btn'),
						clear: get('clear-btn'),
						record: get('record-btn'),
						resetSettings: get('reset-settings'),
						resetCamera: get('reset-camera'),
						sceneLength: get('scene-length-btn'),
						newCamera: get('new-camera-btn'),
						centerToObject: get('center-to-object-btn'), 
						focusToObject: get('focus-to-object-btn'),
						autoKeyframe: get('auto-keyframe'),
						addCamKey: get('add-keyframe'),
						delCamKey: get('delete-keyframe'),
						clearCamKey: get('clear-keyframes'), 
						deleteCustomCamera: get('delete-custom-camera'),
						toggleCamAnim: get('toggle-camera-anim'),
						diagnostic: get('diagnostic-btn'),
						yup: get('y-up-btn')
					},
					inputs: {
						slider: get('slider'),
						fps: get('fps-input'),
						startFrame: get('start-frame'),
						endFrame: get('end-frame'),
						bgColorPicker: get('bg-color-picker'),
						sideSelect: get('side-select'),
						file: get('import-file-input'),
						fov: get('fov-input'),
						near: get('near-input'),
						far: get('far-input'),
						rollAngle: get('roll-angle'),
						views: get('views-select'),
						materialSelect: get('material-mode-select'),
						helperSize: get('helper-size-slider')
					},
					toggles: {
						helper: get('helper-toggle'),
						info: get('info-display-toggle'),
						material: get('material-mode-toggle'),
						light: get('light-mode-toggle'),
						ortho: get('orthographic-toggle'),
						shadows: get('shadows-toggle')
					},
					displays: { 
						frame: get('frame-display')
					}
				};
			}

			init() {
				const w = this.dom.container.clientWidth;
				const h = this.dom.container.clientHeight;
				
				this.renderer = new THREE.WebGLRenderer({
					antialias: true,
					preserveDrawingBuffer: true,
					powerPreference: "default"
				});
				this.renderer.setSize(w, h);
				this.renderer.setPixelRatio(window.devicePixelRatio);
				this.renderer.shadowMap.enabled = this.state.lights.shadowsEnabled;
				this.renderer.shadowMap.type = THREE.VSMShadowMap;	// BasicShadowMap | PCFSoftShadowMap | VSMShadowMap
				this.renderer.shadowMap.autoUpdate = true;
				this.dom.container.appendChild(this.renderer.domElement);
				
				this.createDefaultCameras();
				this.camera = this.state.cameras.default[0];
				this.camera.aspect = w / h;
				this.camera.updateProjectionMatrix();
				this.dom.inputs.views.value = "User";
				
				this.scene = new THREE.Scene();
				this.scene.background = new THREE.Color(this.state.defaultSettings.bgColor);
				this.dom.inputs.bgColorPicker.value = this.state.defaultSettings.bgColor;
				
				this.controls = new OrbitControls(this.camera, this.renderer.domElement);
				this.controls.target.set(0, 1, 0);
				this.controls.enableDamping = false;
				this.controls.update();
				
				this.setupSceneHelpers();
				
				this.state.textureLoader = new THREE.TextureLoader();
				this.initializeMaterialAndLightModes();
				
				this.initMaterialGUI();
				this.initLightGUI();
				this.dom.loading.style.display = 'none';
				
				this.dom.inputs.sideSelect.value = this.state.commonParams.side;
				
				this.updateBgColorPickerState(this.state.materialMode);
				this.setupScrollDragging();
				this.updateTimeSleder();
				this.updateKeyframeButtonsState();
				this.updateAutoAddKeyframeButtonState();
				this.updateInfoDisplay();
				this.updateViewsMenu();
				this.updateCameraUIForMode();
				
				this.bindEvents();
				this.initPostProcessing();
				this.animate();
			}

			bindEvents() {
				const b = this.dom.btns, i = this.dom.inputs, t = this.dom.toggles;
				
				b.import.onclick = () => i.file.click();
				i.file.onchange = (e) => this.handleImportFile(e);
				b.export.onclick = () => this.exportModel();
				b.clear.onclick = () => this.clearScene();
				b.record.onclick = () => this.startRecording();
				t.info.onchange = () => this.toggleInfoDisplay();
				t.helper.onchange = () => this.toggleHelper();
				i.materialSelect.onchange = (e) => this.handleMatChange(e);
				i.bgColorPicker.oninput = () => this.updateSceneBackground();
				i.sideSelect.onchange = (e) => this.updateMaterialSide(e);
				t.light.onchange = () => this.toggleLightMode();
				t.shadows.onchange = () => this.toggleShadows();
				b.resetSettings.onclick = () => this.resetSettings();
				i.helperSize.oninput = () => this.updateHelperSize();
				b.diagnostic.onclick = () => this.ImportDiagnostics();
				
				b.play.onclick = () => this.togglePlay();
				b.reverse.onclick = () => this.toggleReversePlay();
				b.first.onclick = () => this.goToFirstFrame();
				b.last.onclick = () => this.goToLastFrame();
				b.prevKey.onclick = () => this.goToPrevKeyframe();
				b.nextKey.onclick = () => this.goToNextKeyframe();
				b.prevFrame.onclick = () => this.goToPrevFrame();
				b.nextFrame.onclick = () => this.goToNextFrame();
				b.toggleCamAnim.onclick = () => this.toggleCameraAnimation();
				i.fps.oninput = (e) => this.validateNumericInput(e, 'fps');
				i.fps.onkeydown = (e) => { if (e.key === 'Enter') this.applyNumericInput(e, 'fps'); };
				i.fps.onblur = (e) => this.applyNumericInput(e, 'fps');
				i.slider.oninput = (e) => this.onTimeSliderInput(e);
				i.startFrame.oninput = (e) => this.validateNumericInput(e, 'startFrame');
				i.startFrame.onkeydown = (e) => { if (e.key === 'Enter') this.applyNumericInput(e, 'startFrame'); };
				i.startFrame.onblur = (e) => this.applyNumericInput(e, 'startFrame');
				i.endFrame.oninput = (e) => this.validateNumericInput(e, 'endFrame');
				i.endFrame.onkeydown = (e) => { if (e.key === 'Enter') this.applyNumericInput(e, 'endFrame'); };
				i.endFrame.onblur = (e) => this.applyNumericInput(e, 'endFrame');
				b.sceneLength.onclick = () => this.applySceneLength();
				
				i.views.onchange = (e) => this.handleViewChange(e);
				b.centerToObject.onclick = () => this.centerToObject();
				b.focusToObject.onclick = () => this.focusToObject();
				b.newCamera.onclick = () => this.createCustomCamera();
				b.autoKeyframe.onclick = () => this.toggleAutoAddKeyframe();
				b.addCamKey.onclick = () => this.addCameraKeyframe();
				b.delCamKey.onclick = () => this.deleteCurrentKeyframe();
				b.clearCamKey.onclick = () => this.clearCameraKeyframes();
				b.deleteCustomCamera.onclick = () => this.deleteCurrentCustomCamera();
				t.ortho.onchange = () => this.toggleOrthographic();
				b.resetCamera.onclick = () => this.resetCamera();
				b.yup.onclick = () => this.resetYup();
				
				// FOV/Size 输入事件 - 添加 fromUserInput 参数，并同时保存状态
				i.fov.oninput = (e) => {
					this.validateNumericInput(e, 'fov');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.fov.onkeydown = (e) => {
					if (e.key === 'Enter') this.applyNumericInput(e, 'fov', true);
				};
				i.fov.onblur = (e) => this.applyNumericInput(e, 'fov', true);
				
				// Near 输入事件
				i.near.oninput = (e) => {
					this.validateNumericInput(e, 'near');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.near.onkeydown = (e) => {
					if (e.key === 'Enter') this.applyNumericInput(e, 'near');
				};
				i.near.onblur = (e) => this.applyNumericInput(e, 'near');
				
				// Far 输入事件
				i.far.oninput = (e) => {
					this.validateNumericInput(e, 'far');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.far.onkeydown = (e) => {
					if (e.key === 'Enter') this.applyNumericInput(e, 'far');
				};
				i.far.onblur = (e) => this.applyNumericInput(e, 'far');
				
				// Roll angle 输入事件 - 添加 fromUserInput 参数，并同时保存状态
				i.rollAngle.oninput = (e) => {
					this.validateNumericInput(e, 'roll');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.rollAngle.onkeydown = (e) => {
					if (e.key === 'Enter') this.applyNumericInput(e, 'roll', true);
				};
				i.rollAngle.onblur = (e) => this.applyNumericInput(e, 'roll', true);
				
				// OrbitControls 事件监听
				this.controls.addEventListener('end', () => {
					if (this.state.autoAddKeyframeEnabled && this.state.cameras.currentType === 'custom') {
						this.addCameraKeyframe();
					}
				});
				
				// 相机参数变化时保存相机状态
				this.controls.addEventListener('change', () => {
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				});
				
				this.renderer.domElement.addEventListener('wheel', (e) => this.handleCameraWheel(e), { passive: false });
				window.addEventListener('resize', this.debounce(() => this.onWindowResize(), 100));
				window.addEventListener('message', (e) => this.handleMessage(e));
			}

			// 核心控制
			setupScrollDragging() {
				const controls = this.dom.controlsPanel;
				
				// 鼠标拖拽功能
				let isDragging = false, startX, scrollLeft;
				controls.addEventListener('mousedown', (e) => {
					isDragging = true;
					controls.classList.add('grabbing');
					startX = e.pageX - controls.offsetLeft;
					scrollLeft = controls.scrollLeft;
				});
				
				const stop = () => {
					isDragging = false;
					controls.classList.remove('grabbing');
				};
				
				controls.addEventListener('mouseleave', stop);
				controls.addEventListener('mouseup', stop);
				
				controls.addEventListener('mousemove', (e) => {
					if (!isDragging) return;
					e.preventDefault();
					const x = e.pageX - controls.offsetLeft;
					controls.scrollLeft = scrollLeft - (x - startX) * 2;
				}); 
				
				// 滚轮滚动功能 
				controls.addEventListener('wheel', (e) => {
					e.preventDefault();
					// 直接使用 deltaY 控制水平滚动
					controls.scrollLeft += e.deltaY;
				}, { passive: false });
				
				// 阻止子元素的鼠标按下事件冒泡
				controls.querySelectorAll('button, input, select').forEach(el => {
					el.addEventListener('mousedown', (e) => e.stopPropagation());
				});
			}

			debounce(func, wait) { 
				let timeout; 
				
				return function executedFunction(...args) {
					const later = () => {
						clearTimeout(timeout);
						func.apply(this, args);
					};
					
					clearTimeout(timeout);
					timeout = setTimeout(later, wait);
				};
			}

			onWindowResize() {
				const w = this.dom.container.clientWidth;
				const h = this.dom.container.clientHeight;
				
				this.updateInfoDisplay();
				
				if (this.camera && this.renderer) {
					if (this.camera.isOrthographicCamera) {
						// 根据视口高度和新的宽高比更新正交相机的视锥
						const viewHeight = this.camera.userData.viewHeight || (this.camera.top - this.camera.bottom);
						this.updateOrthographicFromViewHeight(this.camera, viewHeight);
					} else {
						this.camera.aspect = w / h;
					}
					this.camera.updateProjectionMatrix();
					this.renderer.setSize(w, h);
					
					if (this.normalRenderTarget) {
						this.normalRenderTarget.setSize(w, h);
					}
					
					if (this.ssaoPass && this.ssaoPass.setSize) {
						this.ssaoPass.setSize(w, h);
					}
					
					if (this.gtaoPass && this.gtaoPass.setSize) {
						this.gtaoPass.setSize(w, h);
					}
					
					// 更新后处理合成器大小
					if (this.composer) {
						// 确保 composer 有有效的 renderTarget
						if (!this.composer.renderTarget1 || !this.composer.renderTarget1.isWebGLRenderTarget) {
							this.initPostProcessing();
						} else {
							this.composer.setSize(w, h);
						}
					}
				}
			}

			async handleMessage(event) {
				if (event.data.type === 'loadData') {
					await this.load3DData(event.data.filename, event.data.format);
				}
			}

			showMessage(message, duration = 3000) {
				this.dom.loading.textContent = message;
				this.dom.loading.style.display = 'block';
				
				if (this._messageTimer) {
					clearTimeout(this._messageTimer);
				}
				
				this._messageTimer = setTimeout(() => {
					if (!this.state.loading) {
						this.dom.loading.style.display = 'none';
					}
				}, duration);
			}

			updateInfoDisplay() {
				if (!this.dom.infoDisplay) return;
				
				let info = '';
				const container = this.dom.container;
				const width = container ? container.clientWidth : 0;
				const height = container ? container.clientHeight : 0;
				
				// 1. 文件名
				if (this.state.currentFileData && this.state.currentFileData.filename) {
					const fileName = this.state.currentFileData.filename.split('/').pop();
					info += fileName + ' | ';
				}
				
				// 2. 分辨率
				info += Math.round(width) + 'x' + Math.round(height);
				
				// 3. 帧数信息
				let sceneFrames = this.state.playback.totalFrames > 1 ? this.state.playback.totalFrames : 0;
				
				// 检查是否有SMPL动画
				let smplFrames = 0;
				if (this.state.smplData && this.state.smplData.numFrames) {
					smplFrames = this.state.smplData.numFrames;
				}
				
				// 如果原始SMPL数据不存在，检查场景中的SMPL帧网格（GLB导入）
				if (smplFrames === 0) {
					const smplMeshes = [];
					this.scene.traverse(child => {
						if (child.isMesh && child.userData && child.userData.isSMPLFrame) {
							smplMeshes.push(child);
						}
					});
					
					if (smplMeshes.length > 0) {
						smplFrames = smplMeshes.length;
						
						// 也更新smplData以便后续使用
						if (!this.state.smplData) {
							this.state.smplData = { numFrames: smplFrames };
						}
					}
				}
				
				// 优先使用SMPL帧数（如果有的话）
				if (smplFrames > 0) {
					sceneFrames = smplFrames;
				}
				
				// 4. 自定义相机动画帧数
				let cameraAnimationFrames = 0;
				let hasCameraAnimation = false;
				
				// 检查所有自定义相机的关键帧
				this.state.cameras.custom.forEach(camera => {
					if (camera.userData.keyframes && camera.userData.keyframes.length >= 2) {
						const cameraKeyframes = camera.userData.keyframes;
						
						// 只有当至少有两个关键帧时才计算
						if (cameraKeyframes.length >= 2) {
							let minFrame = Infinity;
							let maxFrame = -Infinity;
							
							cameraKeyframes.forEach(k => {
								if (k.frame < minFrame) minFrame = k.frame;
								if (k.frame > maxFrame) maxFrame = k.frame;
							});
							
							// 只有当最小帧和最大帧不同，表示有动画范围
							if (minFrame < maxFrame) {
								hasCameraAnimation = true;
								const frameRange = maxFrame - minFrame + 1;
								cameraAnimationFrames = Math.max(cameraAnimationFrames, frameRange);
							}
						}
					}
				});
				
				// 5. 构建帧数显示字符串
				let framesDisplay = '';
				
				if (sceneFrames > 1 && hasCameraAnimation && cameraAnimationFrames > 0) {
					// 既有场景动画又有相机动画：scene [camera] frames
					framesDisplay = ' | ' + sceneFrames + ' [' + cameraAnimationFrames + '] frames';
				} else if (sceneFrames > 1 && (!hasCameraAnimation || cameraAnimationFrames <= 0)) {
					// 只有场景动画：scene frames
					framesDisplay = ' | ' + sceneFrames + ' frames';
				} else if (sceneFrames <= 1 && hasCameraAnimation && cameraAnimationFrames > 0) {
					// 只有相机动画：[camera] frames
					framesDisplay = ' | [' + cameraAnimationFrames + '] frames';
				}
				// 两者都没有，不显示帧数信息
				
				info += framesDisplay;
				
				// 6. 添加相机信息
				let cameraInfo = '';
				let modeInfo = '';
				
				if (this.camera) {
					const cameraName = this.camera.name || 'Unnamed';
					
					// 根据相机类型设置显示文本
					if (this.state.cameras.currentType === 'default') {
						// 默认相机不显示模式
					} else if (this.state.cameras.currentType === 'custom') {
						// 自定义相机：根据 cameraAnim.isEnabled 显示模式
						modeInfo = this.state.cameraAnim.isEnabled ? ' [Play Mode]' : ' [Edit Mode]';
					} else if (this.state.cameras.currentType === 'scene') {
						// 场景相机：总是显示 Play Mode
						modeInfo = ' [Play Mode]';
					}
					
					cameraInfo = ' | ' + cameraName + modeInfo;
				} else {
					cameraInfo = ' | Camera: None';
				}
				
				info += cameraInfo;
				
				// 7. 添加FPS信息（如果有）
				if (this.fps && this.fps.value > 0) {
					info += ' | ' + this.fps.value + ' FPS';
				} else {
					info += ' | 0 FPS';
				}
				
				this.dom.infoDisplay.textContent = info;
			}

			updateFPSInfo() {
				const currentTime = performance.now();
				this.fps.frameCount++;
				
				const timePassed = currentTime - this.fps.lastUpdateTime;
				
				if (timePassed >= this.fps.updateInterval) {
					this.fps.value = Math.round((this.fps.frameCount * 1000) / timePassed);
					this.fps.frameCount = 0;
					this.fps.lastUpdateTime = currentTime;
					
					this.updateInfoDisplay();
				}
			}

			setupSceneHelpers() {
				// 创建网格辅助
				this.state.grid = new THREE.GridHelper(10, 10, 0x444444, 0x222222);
				this.state.grid.name = "GridHelper";
				this.scene.add(this.state.grid);
				
				// 创建坐标轴辅助
				this.state.axesHelper = new THREE.AxesHelper(0.5);
				this.state.axesHelper.name = "AxesHelper";
				this.scene.add(this.state.axesHelper);
				
				// 创建默认灯光
				this.createDefaultLights();
				
				// 为方向光创建可视化（环境光不需要）
				this.createLightVisualization(this.state.lights.dir);
				
				// 初始可见性设置
				const isGrid = this.dom.toggles.helper.checked;
				const useSceneLight = this.state.useSceneLight;
				
				this.state.lights.dir.visible = !useSceneLight;
				this.state.lights.amb.visible = !useSceneLight;
				
				if (this.state.lights.dir.userData.sphereVisualization) {
					this.state.lights.dir.userData.sphereVisualization.visible = !useSceneLight && isGrid;
				}
			}

			updateHelperSize() {
				const slider = this.dom.inputs.helperSize;
				if (!slider) return;
				
				const value = parseFloat(slider.value);
				this.state.helperSize = value;
				
				this.updateAllVisualizationSizes();
			}

			toggleHelper() {
				const vis = this.dom.toggles.helper.checked;
				if(this.state.grid) this.state.grid.visible = vis;
				if(this.state.axesHelper) this.state.axesHelper.visible = vis;
				this.updateVisualizationVisibility();
			}

			toggleInfoDisplay() {
				const isChecked = this.dom.toggles.info.checked;
				
				this.dom.infoDisplay.style.display = isChecked ? 'block' : 'none';
				
				if (isChecked) {
					this.showMaterialFolder(this.state.materialMode);
					
					if (!this.state.useSceneLight && (this.state.materialMode === 'original' || this.state.materialMode === 'default')) {
						this.showLightGUI();
					} else {
						this.hideLightGUI();
					}
				} else {
					this.hideMaterialGUI();
					this.hideLightGUI();
				}
			}

			// 材质GUI
			initMaterialGUI() {
				// 创建GUI容器
				this.state.materialGUI.container = document.createElement('div');
				this.state.materialGUI.container.id = 'material-gui';
				this.state.materialGUI.container.className = 'material-gui-container';
				this.state.materialGUI.container.style.display = 'none';
				
				// 将GUI容器添加到页面（放在info display后面）
				if (this.dom.infoDisplay && this.dom.infoDisplay.parentNode) {
					this.dom.infoDisplay.parentNode.insertBefore(
						this.state.materialGUI.container,
						this.dom.infoDisplay.nextSibling
					);
				} else {
					// 如果找不到info display，添加到body
					document.body.appendChild(this.state.materialGUI.container);
				}
				
				// 创建GUI实例
				if (typeof lil !== 'undefined' && lil.GUI) {
					this.createMaterialGUI();
				} else {
					this.loadMaterialGUI();
				}
			}

			loadMaterialGUI() {
				const script = document.createElement('script');
				script.src = 'https://cdn.jsdelivr.net/npm/lil-gui@0.19.2/dist/lil-gui.umd.js';
				script.onload = () => {
					this.createMaterialGUI();
				};
				script.onerror = () => {
				};
				document.head.appendChild(script);
			}

			createMaterialGUI() {
				// 检查lil-gui是否可用
				if (typeof lil === 'undefined' || !lil.GUI) {
					this.loadMaterialGUI();
					return;
				}
				
				// 如果GUI实例已存在，先销毁
				if (this.state.materialGUI.guiInstance) {
					try {
						this.state.materialGUI.guiInstance.destroy();
					} catch (e) {
						console.log('Error destroying old GUI:', e);
					}
					this.state.materialGUI.guiInstance = null;
				}
				
				try {
					// 创建新的GUI实例 - 不自动放置
					this.state.materialGUI.guiInstance = new lil.GUI({
						container: this.state.materialGUI.container,
						autoPlace: false,
						width: 180,
						title: ''
					});
					
					// 获取GUI根元素并应用更紧凑的样式
					const guiRoot = this.state.materialGUI.container.querySelector('.lil-gui');
					if (guiRoot) {
						guiRoot.style.width = '100%';
						guiRoot.style.maxHeight = '300px';
						guiRoot.style.overflowY = 'auto';
						guiRoot.style.padding = '0';
						guiRoot.style.margin = '0';
						
						// 隐藏标题栏
						const titleBar = guiRoot.querySelector('.title');
						if (titleBar) {
							titleBar.style.display = 'none';
						}
					}
					
					// 创建材质参数文件夹
					this.state.materialGUI.commonFolder = null;
					this.state.materialGUI.defaultFolder = null;
					this.state.materialGUI.normalFolder = null;
					this.state.materialGUI.wireframeFolder = null;
					this.state.materialGUI.lineartFolder = null;
					this.state.materialGUI.edgeFolder = null;
					this.state.materialGUI.cannyFolder = null;
					this.state.materialGUI.contourFolder = null;
					this.state.materialGUI.ssaoFolder = null;
					this.state.materialGUI.gtaoFolder = null;
					
				} catch (error) {
					console.error('Error creating GUI:', error);
				}
			}

			showMaterialGUI() {
				if (!this.state.materialGUI.container) return;
				this.state.materialGUI.container.style.display = 'block';
				this.state.materialGUI.visible = true;
			}

			hideMaterialGUI() {
				if (!this.state.materialGUI.container) return;
				this.state.materialGUI.container.style.display = 'none';
				this.state.materialGUI.visible = false;
			}

			showMaterialFolder(mode) {
				// 隐藏所有材质文件夹
				this.hideAllMaterialFolders();
				
				// 显示对应的材质文件夹
				switch(mode) {
					case 'original':
						// original模式不显示材质参数文件夹
						break;
					case 'default':
						this.createDefaultMaterialFolder();
						break;
					case 'normal':
						this.createNormalMaterialFolder();
						break;
					case 'depth':
						// depth模式不需要GUI参数
						break;
					case 'wireframe':
						this.createWireframeMaterialFolder();
						break;
					case 'lineart':
						this.createLineArtMaterialFolder();
						break;
					case 'edge':
						this.createEdgeMaterialFolder();
						break;
					case 'canny':
						this.createCannyMaterialFolder();
						break;
					case 'contour':
						this.createContourMaterialFolder();
						break;
					case 'ssao':
						this.createSSAOGUIFolder();
						break;
					case 'gtao':
						this.createGTAOGUIFolder();
						break;
				}
				
				// 显示GUI容器（如果有参数文件夹）
				if (mode !== 'original' && mode !== 'depth') {
					this.showMaterialGUI();
				} else {
					this.hideMaterialGUI();
				}
			}

			hideAllMaterialFolders() {
				const folders = [
					'defaultFolder', 'normalFolder', 'wireframeFolder', 'lineartFolder',
					'edgeFolder', 'cannyFolder', 'contourFolder', 'ssaoFolder', 'gtaoFolder'
				];
				
				folders.forEach(folderName => {
					const folder = this.state.materialGUI[folderName];
					if (folder) {
						try {
							folder.destroy();
						} catch (e) {
							console.log('Error destroying folder:', folderName, e);
						}
						this.state.materialGUI[folderName] = null;
					}
				});
			}

			createDefaultMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.defaultFolder) {
					try {
						this.state.materialGUI.defaultFolder.destroy();
					} catch (e) {
						console.log('Error destroying default folder:', e);
					}
					this.state.materialGUI.defaultFolder = null;
				}
				
				this.state.materialGUI.defaultFolder = this.state.materialGUI.guiInstance.addFolder('Default Material');
				
				this.state.materialGUI.defaultFolder.addColor(this.state.materialParams.default, 'color')
					.onChange((value) => {
						this.state.materialParams.default.color = value;
						this.updateDefaultMaterial();
					}).name('Color');
				
				this.state.materialGUI.defaultFolder.add(this.state.materialParams.default, 'roughness', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.default.roughness = value;
						this.updateDefaultMaterial();
					}).name('Roughness');
				
				this.state.materialGUI.defaultFolder.add(this.state.materialParams.default, 'metalness', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.default.metalness = value;
						this.updateDefaultMaterial();
					}).name('Metalness');
				
				this.state.materialGUI.defaultFolder.add(this.state.materialParams.default, 'flatShading')
					.onChange((value) => {
						this.state.materialParams.default.flatShading = value;
						this.updateDefaultMaterial();
					}).name('Flat Shading');
				
				this.state.materialGUI.defaultFolder.add({
					reset: () => this.resetDefaultParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.defaultFolder.open();
			}

			createWireframeMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.wireframeFolder) {
					try {
						this.state.materialGUI.wireframeFolder.destroy();
					} catch (e) {
						console.log('Error destroying wireframe folder:', e);
					}
					this.state.materialGUI.wireframeFolder = null;
				}
				
				this.state.materialGUI.wireframeFolder = this.state.materialGUI.guiInstance.addFolder('Wireframe Material');
				
				this.state.materialGUI.wireframeFolder.addColor(this.state.materialParams.wireframe, 'color')
					.onChange((value) => {
						this.state.materialParams.wireframe.color = value;
						this.updateWireframeMaterial();
					}).name('Wireframe Color');
				
				this.state.materialGUI.wireframeFolder.add(this.state.materialParams.wireframe, 'linewidth', 0.1, 5, 0.1)
					.onChange((value) => {
						this.state.materialParams.wireframe.linewidth = value;
						this.updateWireframeMaterial();
					}).name('Line Width');
				
				this.state.materialGUI.wireframeFolder.add(this.state.materialParams.wireframe, 'opacity', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.wireframe.opacity = value;
						this.updateWireframeMaterial();
					}).name('Opacity');
				
				this.state.materialGUI.wireframeFolder.add({
					reset: () => this.resetWireframeParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.wireframeFolder.open();
			}

			createNormalMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.normalFolder) {
					try {
						this.state.materialGUI.normalFolder.destroy();
					} catch (e) {
						console.log('Error destroying normal folder:', e);
					}
					this.state.materialGUI.normalFolder = null;
				}
				
				this.state.materialGUI.normalFolder = this.state.materialGUI.guiInstance.addFolder('Normal Material');
				
				this.state.materialGUI.normalFolder.add(this.state.materialParams.normal, 'flatShading')
					.onChange((value) => {
						this.state.materialParams.normal.flatShading = value;
						this.updateNormalMaterial();
					}).name('Flat Shading');
				
				this.state.materialGUI.normalFolder.add({
					reset: () => this.resetNormalParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.normalFolder.open();
			}

			createLineArtMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.lineartFolder) {
					try {
						this.state.materialGUI.lineartFolder.destroy();
					} catch (e) {
						console.log('Error destroying lineart folder:', e);
					}
					this.state.materialGUI.lineartFolder = null;
				}
				
				this.state.materialGUI.lineartFolder = this.state.materialGUI.guiInstance.addFolder('Lineart Material');
				
				this.state.materialGUI.lineartFolder.addColor(this.state.materialParams.lineart, 'color')
					.onChange((value) => {
						this.state.materialParams.lineart.color = value;
						this.updateLineartMaterial();
					}).name('Color');
				
				this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'edgeStart', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.edgeStart = value;
						this.updateLineartMaterial();
					}).name('Edge Start');
				
				this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'edgeEnd', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.edgeEnd = value;
						this.updateLineartMaterial();
					}).name('Edge End');
				
				this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'curvatureStart', 0, 0.1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.curvatureStart = value;
						this.updateLineartMaterial();
					}).name('Curvature Start');
				
				this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'curvatureEnd', 0, 0.1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.curvatureEnd = value;
						this.updateLineartMaterial();
					}).name('Curvature End');
				
				this.state.materialGUI.lineartFolder.add({
					reset: () => this.resetLineartParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.lineartFolder.open();
			}

			createCannyMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.cannyFolder) {
					try { this.state.materialGUI.cannyFolder.destroy(); } catch(e) {}
					this.state.materialGUI.cannyFolder = null;
				}
				
				this.state.materialGUI.cannyFolder = this.state.materialGUI.guiInstance.addFolder('Canny Material');
				
				this.state.materialGUI.cannyFolder.addColor(this.state.materialParams.canny, 'color')
					.onChange((value) => {
						this.state.materialParams.canny.color = value;
						this.updateCannyMaterial();
					}).name('Color');
				
				this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'lowThreshold', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.lowThreshold = value;
						this.updateCannyMaterial();
					}).name('Low Threshold');
				
				this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'highThreshold', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.highThreshold = value;
						this.updateCannyMaterial();
					}).name('High Threshold');
				
				this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'edgeStrength', 0, 5, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.edgeStrength = value;
						this.updateCannyMaterial();
					}).name('Edge Strength');
				
				this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'edgeDetail', 0.1, 0.9, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.edgeDetail = value;
						this.updateCannyMaterial();
					}).name('Edge Detail');
				
				this.state.materialGUI.cannyFolder.add({
					reset: () => this.resetCannyParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.cannyFolder.open();
			}

			createEdgeMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.edgeFolder) {
					try { this.state.materialGUI.edgeFolder.destroy(); } catch(e) {}
					this.state.materialGUI.edgeFolder = null;
				}
				
				this.state.materialGUI.edgeFolder = this.state.materialGUI.guiInstance.addFolder('Edge Material');
				
				this.state.materialGUI.edgeFolder.addColor(this.state.materialParams.edge, 'color')
					.onChange((value) => {
						this.state.materialParams.edge.color = value;
						this.updateEdgeMaterial();
					}).name('Color');
				
				this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'normalThreshold', 0, 4, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.normalThreshold = value;
						this.updateEdgeMaterial();
					}).name('Normal Threshold');
				
				this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'posThreshold', 0, 4, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.posThreshold = value;
						this.updateEdgeMaterial();
					}).name('Position Threshold');
				
				this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'edgeStart', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.edgeStart = value;
						this.updateEdgeMaterial();
					}).name('Edge Start');
				
				this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'edgeEnd', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.edgeEnd = value;
						this.updateEdgeMaterial();
					}).name('Edge End');
				
				this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'contrast', 1, 2, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.contrast = value;
						this.updateEdgeMaterial();
					}).name('Contrast');
				
				this.state.materialGUI.edgeFolder.add({
					reset: () => this.resetEdgeParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.edgeFolder.open();
			}

			createContourMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.contourFolder) {
					try {
						this.state.materialGUI.contourFolder.destroy();
					} catch (e) {
						console.log('Error destroying contour folder:', e);
					}
					this.state.materialGUI.contourFolder = null;
				}
				
				this.state.materialGUI.contourFolder = this.state.materialGUI.guiInstance.addFolder('Contour Material');
				
				this.state.materialGUI.contourFolder.addColor(this.state.materialParams.contour, 'color')
					.onChange((value) => {
						this.state.materialParams.contour.color = value;
						this.updateContourMaterial();
					}).name('Color');
				
				this.state.materialGUI.contourFolder.add(this.state.materialParams.contour, 'thickness', 0.5, 5, 0.01)
					.onChange((value) => {
						this.state.materialParams.contour.thickness = value;
						this.updateContourMaterial();
					}).name('Thickness');
				
				this.state.materialGUI.contourFolder.add(this.state.materialParams.contour, 'depthThreshold', 0.01, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.contour.depthThreshold = value;
						this.updateContourMaterial();
					}).name('Depth Threshold');
				
				this.state.materialGUI.contourFolder.add(this.state.materialParams.contour, 'normalThreshold', 0.01, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.contour.normalThreshold = value;
						this.updateContourMaterial();
					}).name('Normal Threshold');
				
				this.state.materialGUI.contourFolder.add({
					reset: () => this.resetContourParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.contourFolder.open();
			}

			createSSAOGUIFolder() {
				if (!this.ssaoPass || !this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.ssaoFolder) {
					try {
						this.state.materialGUI.ssaoFolder.destroy();
					} catch (e) {
						console.log('Error destroying SSAO folder:', e);
					}
					this.state.materialGUI.ssaoFolder = null;
				}
				
				this.state.materialGUI.ssaoFolder = this.state.materialGUI.guiInstance.addFolder('SSAO Settings');
				
				const ssaoParams = this.state.postProcessingParams.ssao;
				
				this.state.materialGUI.ssaoFolder.add(ssaoParams, 'kernelRadius', 0, 32, 0.5)
					.onChange((value) => {
						ssaoParams.kernelRadius = value;
						this.updateSSAOParameters();
					}).name('Kernel Radius');
				
				this.state.materialGUI.ssaoFolder.add(ssaoParams, 'minDistance', 0.001, 0.02, 0.001)
					.onChange((value) => {
						ssaoParams.minDistance = value;
						this.updateSSAOParameters();
					}).name('Min Distance');
				
				this.state.materialGUI.ssaoFolder.add(ssaoParams, 'maxDistance', 0.01, 0.3, 0.01)
					.onChange((value) => {
						ssaoParams.maxDistance = value;
						this.updateSSAOParameters();
					}).name('Max Distance');
				
				this.state.materialGUI.ssaoFolder.add({
					reset: () => this.resetSSAOParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.ssaoFolder.open();
			}

			createGTAOGUIFolder() {
				if (!this.gtaoPass || !this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.gtaoFolder) {
					try {
						this.state.materialGUI.gtaoFolder.destroy();
					} catch (e) {
						console.log('Error destroying GTAO folder:', e);
					}
					this.state.materialGUI.gtaoFolder = null;
				}
				
				this.state.materialGUI.gtaoFolder = this.state.materialGUI.guiInstance.addFolder('GTAO Settings');
				
				const gtaoParams = this.state.postProcessingParams.gtao;
				
				this.state.materialGUI.gtaoFolder.add(gtaoParams, 'radius', 0.01, 1, 0.01)
					.onChange((value) => {
						gtaoParams.radius = value;
						this.UpdateGTAOParameters();
					}).name('Radius');
				
				this.state.materialGUI.gtaoFolder.add(gtaoParams, 'distanceExponent', 1, 4, 0.1)
					.onChange((value) => {
						gtaoParams.distanceExponent = value;
						this.UpdateGTAOParameters();
					}).name('Distance Exponent');
				
				this.state.materialGUI.gtaoFolder.add(gtaoParams, 'thickness', 0.01, 10, 0.01)
					.onChange((value) => {
						gtaoParams.thickness = value;
						this.UpdateGTAOParameters();
					}).name('Thickness');
				
				this.state.materialGUI.gtaoFolder.add(gtaoParams, 'scale', 0.01, 2.0, 0.01)
					.onChange((value) => {
						gtaoParams.scale = value;
						this.UpdateGTAOParameters();
					}).name('Scale');
				
				this.state.materialGUI.gtaoFolder.add(gtaoParams, 'distanceFallOff', 0, 1, 0.01)
					.onChange((value) => {
						gtaoParams.distanceFallOff = value;
						this.UpdateGTAOParameters();
					}).name('Distance Falloff');
				
				this.state.materialGUI.gtaoFolder.add(gtaoParams, 'samples', 2, 32, 1)
					.onChange((value) => {
						gtaoParams.samples = value;
						this.UpdateGTAOParameters();
					}).name('Samples');
				
				this.state.materialGUI.gtaoFolder.add({
					reset: () => this.resetGTAOParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.gtaoFolder.open();
			}

			// 灯光GUI
			initLightGUI() {
				// 创建灯光GUI容器
				this.state.lightGUI.container = document.createElement('div');
				this.state.lightGUI.container.id = 'light-gui';
				this.state.lightGUI.container.className = 'light-gui-container';
				this.state.lightGUI.container.style.display = 'none';
				
				// 将灯光GUI容器添加到页面（放在材质GUI前面）
				if (this.state.materialGUI.container && this.state.materialGUI.container.parentNode) {
					this.state.materialGUI.container.parentNode.insertBefore(
						this.state.lightGUI.container,
						this.state.materialGUI.container
					);
				} else if (this.dom.infoDisplay && this.dom.infoDisplay.parentNode) {
					this.dom.infoDisplay.parentNode.insertBefore(
						this.state.lightGUI.container,
						this.dom.infoDisplay.nextSibling
					);
				} else {
					document.body.appendChild(this.state.lightGUI.container);
				}
				
				// 确保lil-gui已加载
				if (typeof lil !== 'undefined' && lil.GUI) {
					this.createLightGUI();
				} else {
					this.loadLightGUI();
				}
			}

			loadLightGUI() {
				const script = document.createElement('script');
				script.src = 'https://cdn.jsdelivr.net/npm/lil-gui@0.19.2/dist/lil-gui.umd.js';
				script.onload = () => {
					this.createLightGUI();
				};
				script.onerror = () => {
				};
				document.head.appendChild(script);
			}

			createLightGUI() {
				// 检查lil-gui是否可用
				if (typeof lil === 'undefined' || !lil.GUI) {
					this.loadLightGUI();
					return;
				}
				
				// 如果GUI实例已存在，先销毁
				if (this.state.lightGUI.guiInstance) {
					try {
						this.state.lightGUI.guiInstance.destroy();
					} catch (e) {
						console.log('Error destroying old light GUI:', e);
					}
					this.state.lightGUI.guiInstance = null;
				}
				
				try {
					// 创建新的GUI实例
					this.state.lightGUI.guiInstance = new lil.GUI({
						container: this.state.lightGUI.container,
						autoPlace: false,
						width: 180,
						title: ''
					});
					
					// 获取GUI根元素并应用样式
					const guiRoot = this.state.lightGUI.container.querySelector('.lil-gui');
					if (guiRoot) {
						guiRoot.style.width = '100%';
						guiRoot.style.maxHeight = '524px';
						guiRoot.style.overflowY = 'auto';
						guiRoot.style.padding = '0';
						guiRoot.style.margin = '0';
						
						// 修改标题栏样式
						const titleBar = guiRoot.querySelector('.title');
						if (titleBar) {
							titleBar.style.display = 'none';
						}
					}
					
					// 创建灯光参数
					this.createDirLightFolder();
					this.createAmbLightFolder();
					
					// 初始状态：根据当前灯光模式设置可见性
					this.toggleLightGUI();
					
				} catch (error) {
					console.error('Error creating light GUI:', error);
				}
			}

			showLightGUI() {
				if (!this.state.lightGUI.container) return;
				this.state.lightGUI.container.style.display = 'block';
				this.state.lightGUI.visible = true;
			}

			hideLightGUI() {
				if (!this.state.lightGUI.container) return;
				this.state.lightGUI.container.style.display = 'none';
				this.state.lightGUI.visible = false;
			}

			toggleLightGUI() {
				// 只有在默认灯光和原始|默认材质模式下才显示
				if (!this.state.useSceneLight && (this.state.materialMode === 'original' || this.state.materialMode === 'default')) {
					this.showLightGUI();
				} else {
					this.hideLightGUI();
				}
			}

			createDirLightFolder() {
				if (!this.state.lightGUI.guiInstance) return;
				
				// 如果已存在文件夹，先销毁
				if (this.state.lightGUI.dirLightFolder) {
					try {
						this.state.lightGUI.dirLightFolder.destroy();
					} catch (e) {
						console.log("Error destroying existing folder:", e);
					}
					this.state.lightGUI.dirLightFolder = null;
				}
				
				// 方向光文件夹
				const dirLightFolder = this.state.lightGUI.guiInstance.addFolder('Directional Light');
				
				// 保存文件夹引用到状态
				this.state.lightGUI.dirLightFolder = dirLightFolder;
				
				dirLightFolder.addColor(this.state.lights, 'dirColor')
					.onChange((value) => {
						this.state.lights.dirColor = value;
						this.updateDirLightColor();
					}).name('Dir Color');
				
				dirLightFolder.add(this.state.lights, 'dirIntensity', 0, 5, 0.01)
					.onChange((value) => {
						this.state.lights.dirIntensity = value;
						this.updateDirLightIntensity();
					}).name('Dir Intensity');
				
				dirLightFolder.add({
					reset: () => this.resetDirLightParameters('main')
				}, 'reset').name('Reset');
				
				dirLightFolder.add(this.state.lights.dirSpherical, 'azimuth', 0, 360, 0.01)
					.onChange((value) => {
						this.state.lights.dirSpherical.azimuth = value;
						this.updateDirLightFromSpherical();
					}).name('Azimuth');
				
				dirLightFolder.add(this.state.lights.dirSpherical, 'elevation', -90, 90, 0.01)
					.onChange((value) => {
						this.state.lights.dirSpherical.elevation = value;
						this.updateDirLightFromSpherical();
					}).name('Elevation');
				
				dirLightFolder.add(this.state.lights.dirSpherical, 'radius', 1, 1000, 0.01)
					.onChange((value) => {
						this.state.lights.dirSpherical.radius = value;
						this.updateDirLightFromSpherical();
					}).name('Distance');
				
				dirLightFolder.add({
					reset: () => this.resetDirLightParameters('pose')
				}, 'reset').name('Reset Pose');
				
				/* 
				dirLightFolder.add(this.state.lights, 'shadowType', {
					'Basic': 'basic',
					'PCF': 'pcf',
					'PCF Soft': 'pcfsoft',
					'VSM': 'vsm'
				}).onChange((value) => {
					this.state.lights.shadowSettings.shadowType = value;
					this.updateShadowType();
				}).name('Shadow Type');
				
				dirLightFolder.add(this.state.lights.shadowSettings, 'mapSize', [512, 1024, 2048, 4096])
					.onChange((value) => {
						this.state.lights.shadowSettings.mapSize = value;
						this.updateShadowSettings();
					}).name('Shadow Map Size');
				
				dirLightFolder.add(this.state.lights.shadowSettings, 'radius', 0, 10, 1)
					.onChange((value) => {
						this.state.lights.shadowSettings.radius = value;
						this.updateShadowSettings();
					}).name('Shadow Blur Radius');
				
				dirLightFolder.add(this.state.lights.shadowSettings, 'samples', 1, 32, 1)
					.onChange((value) => {
						this.state.lights.shadowSettings.samples = value;
						this.updateShadowSettings();
					}).name('Shadow Blur Samples');
				 */
				dirLightFolder.add(this.state.lights.shadowSettings, 'bias', -0.01, 0.01, 0.0001)
					.onChange((value) => {
						this.state.lights.shadowSettings.bias = value;
						this.updateShadowSettings();
						}).name('Shadow Bias');
				
				dirLightFolder.add(this.state.lights.shadowSettings, 'normalBias', 0, 0.1, 0.001)
					.onChange((value) => {
						this.state.lights.shadowSettings.normalBias = value;
						this.updateShadowSettings();
					}).name('Shadow Normal Bias');
				
				dirLightFolder.add(this.state.lights.shadowSettings.camera, 'near', 0.01, 100, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.near = value;
						this.updateShadowSettings();
					}).name('Shadow Near');
				
				dirLightFolder.add(this.state.lights.shadowSettings.camera, 'far', 10, 2000, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.far = value;
						this.updateShadowSettings();
					}).name('Shadow Far');
				
				dirLightFolder.add(this.state.lights.shadowSettings.camera, 'left', -1000, 0, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.left = value;
						this.updateShadowSettings();
					}).name('Shadow Left');
				
				dirLightFolder.add(this.state.lights.shadowSettings.camera, 'right', 0, 1000, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.right = value;
						this.updateShadowSettings();
					}).name('Shadow Right');
				
				dirLightFolder.add(this.state.lights.shadowSettings.camera, 'top', 0, 1000, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.top = value;
						this.updateShadowSettings();
					}).name('Shadow Top');
				
				dirLightFolder.add(this.state.lights.shadowSettings.camera, 'bottom', -1000, 0, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.bottom = value;
						this.updateShadowSettings();
					}).name('Shadow Bottom');
				
				dirLightFolder.add({
					reset: () => this.resetDirLightParameters('shadow')
				}, 'reset').name('Reset Shadow Map');
				
				dirLightFolder.open();
			}

			createAmbLightFolder() {
				if (!this.state.lightGUI.guiInstance) return;
				
				// 如果已存在文件夹，先销毁
				if (this.state.lightGUI.ambLightFolder) {
					try {
						this.state.lightGUI.ambLightFolder.destroy();
					} catch (e) {
						console.log("Error destroying existing folder:", e);
					}
					this.state.lightGUI.ambLightFolder = null;
				}
				
				const ambLightFolder = this.state.lightGUI.guiInstance.addFolder('Ambient Light');
				
				// 保存文件夹引用到状态
				this.state.lightGUI.ambLightFolder = ambLightFolder;
				
				ambLightFolder.addColor(this.state.lights, 'ambColor')
					.onChange((value) => {
						this.state.lights.ambColor = value;
						this.updateAmbLightColor();
					}).name('Amb Color');
				
				ambLightFolder.add(this.state.lights, 'ambIntensity', 0, 5, 0.01)
					.onChange((value) => {
						this.state.lights.ambIntensity = value;
						this.updateAmbLightIntensity();
					}).name('Amb Intensity');
				
				ambLightFolder.add({
					reset: () => this.resetAmbLightParameters()
				}, 'reset').name('Reset');
				
				ambLightFolder.open();
			}

			// 数值输入控制
			validateNumericInput(event, paramName) {
				const input = event.target;
				let value = paramName === 'fps' ? parseInt(input.value) : parseFloat(input.value);
				
				input.classList.remove('invalid');
				input.style.borderColor = '';
				
				// 检查是否是有效数字
				if (isNaN(value)) {
					input.classList.add('invalid');
					input.style.borderColor = 'var(--danger-color)';
					return false;
				}
				
				// 添加pending状态
				input.classList.add('pending');
				input.style.borderColor = 'var(--primary-color)';
				
				return true;
			}

			applyNumericInput(event, paramName, fromUserInput = false) {
				const input = event.target;
				let value = paramName === 'fps' ? parseInt(input.value) : parseFloat(input.value);
				
				input.classList.remove('pending', 'invalid');
				input.style.borderColor = '';
				
				if (isNaN(value)) {
					this.updateCameraUIForMode();
					this.updateTimeSleder();
					return;
				}
				
				switch(paramName) {
					case 'fps':
						if (value < 1) value = 1;
						else if (value > 120) value = 120;
						value = Math.floor(value);
						input.value = value.toString();
						break;
					case 'fov':
						if (this.camera.isOrthographicCamera) {
							if (value < 0.01) value = 0.01;
							else if (value > 1000) value = 1000;
						} else {
							if (value < 0.01) value = 0.01;
							else if (value > 179.99) value = 179.99;
						}
						input.value = value.toFixed(2);
						this.updateCameraFOV();
						break;
					case 'near':
						if (value < 0.01) value = 0.01;
						else if (value > 5000) value = 5000;
						input.value = value.toFixed(2);
						this.updateCameraNear();
						this.dom.inputs.far.min = (value + 0.01).toFixed(2);
						if (parseFloat(this.dom.inputs.far.value) < value + 0.01) {
							this.dom.inputs.far.value = (value + 0.01).toFixed(2);
							this.applyNumericInput({
								target: this.dom.inputs.far
							}, 'far');
						}
						break;
					case 'far':
						const nearValue = parseFloat(this.dom.inputs.near.value);
						const minFar = nearValue + 0.01;
						if (value < minFar) value = minFar;
						else if (value > 5000) value = 5000;
						input.value = value.toFixed(2);
						this.updateCameraFar();
						break;
					case 'startFrame':
						if (value < -9999) value = -9999;
						else if (value > 9999) value = 9999;
						break;
					case 'endFrame':
						const startFrameVal = parseFloat(this.dom.inputs.startFrame.value);
						if (value < startFrameVal) value = startFrameVal;
						else if (value > 9999) value = 9999;
						break;
					case 'roll':
						if (value < -180) value = -180;
						else if (value > 180) value = 180;
						input.value = value.toFixed(2);
						break;
				}
				
				input.value = value.toFixed(2);
				
				switch(paramName) {
					case 'fps':
						this.updateFPS();
						break;
					case 'fov':
						this.updateCameraFOV();
						break;
					case 'near':
						this.updateCameraNear();
						break;
					case 'far':
						this.updateCameraFar();
						break;
					case 'startFrame':
					case 'endFrame':
						this.applyFrameRange();
						break;
					case 'roll':
						this.applyRollAngle();
						break;
				}
				
				if (fromUserInput && 
					this.state.cameras.currentType === 'custom' && 
					this.state.autoAddKeyframeEnabled &&
					(paramName === 'fov' || paramName === 'roll')) {
					this.addCameraKeyframe();
				}
			}

			// 关键帧插值计算
			catmullRomInterpolate(t, p0, p1, p2, p3) {
				const t2 = t * t;
				const t3 = t2 * t;
				
				const result = 0.5 * (
					(2 * p1) + 
					(-p0 + p2) * t + 
					(2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + 
					(-p0 + 3 * p1 - 3 * p2 + p3) * t3
				);
				
				return result;
			}

			catmullRomInterpolateVector3(t, v0, v1, v2, v3) {
				const x = this.catmullRomInterpolate(t, v0.x, v1.x, v2.x, v3.x);
				const y = this.catmullRomInterpolate(t, v0.y, v1.y, v2.y, v3.y);
				const z = this.catmullRomInterpolate(t, v0.z, v1.z, v2.z, v3.z);
				
				return new THREE.Vector3(x, y, z);
			}

			catmullRomInterpolateEuler(t, e0, e1, e2, e3) {
				var interpolateAngle = function(t, a0, a1, a2, a3) {
					var normalizeAngle = function(angle) {
						while (angle > Math.PI) angle -= 2 * Math.PI;
						while (angle < -Math.PI) angle += 2 * Math.PI;
						return angle;
					};
					a0 = normalizeAngle(a0); a1 = normalizeAngle(a1); a2 = normalizeAngle(a2); a3 = normalizeAngle(a3);
					return this.catmullRomInterpolate(t, a0, a1, a2, a3);
				}.bind(this);
				return new THREE.Euler(
					interpolateAngle(t, e0.x, e1.x, e2.x, e3.x),
					interpolateAngle(t, e0.y, e1.y, e2.y, e3.y),
					interpolateAngle(t, e0.z, e1.z, e2.z, e3.z)
				);
			}

			normalizeAngle(angle) {
				angle = angle % 360;
				if (angle > 180) angle -= 360;
				if (angle < -180) angle += 360;
				return angle;
			}

			catmullRomInterpolateAngle(t, a0, a1, a2, a3) {
				// 1. 展开角度序列，确保连续性
				const angles = [a0, a1, a2, a3];
				
				// 展开角度，确保连续性（解决360°边界问题）
				for (let i = 1; i < angles.length; i++) {
					let diff = angles[i] - angles[i-1];
					
					// 确保角度差在[-180, 180]范围内（最短路径）
					while (diff > 180) diff -= 360;
					while (diff < -180) diff += 360;
					
					// 累积角度，形成连续序列
					angles[i] = angles[i-1] + diff;
				}
				
				// 2. 对连续角度序列应用Catmull-Rom插值
				const interpolated = this.catmullRomInterpolate(t, angles[0], angles[1], angles[2], angles[3]);
				
				// 3. 规范化到[-180,180]范围
				return this.normalizeAngle(interpolated);
			}

			lerpAngle(a, b, t) {
				// 将角度标准化到 [-180, 180]
				a = this.normalizeAngle(a);
				b = this.normalizeAngle(b);
				
				// 计算差值，选择最短路径
				let diff = b - a;
				if (diff > 180) {
					diff -= 360;
				} else if (diff < -180) {
					diff += 360;
				}
				
				// 线性插值并标准化
				const result = a + diff * t;
				return this.normalizeAngle(result);
			}

			// 关键帧格式转换
			convertToVector3(value, defaultValue) {
				if (!value) {
					return defaultValue.clone();
				}
				
				if (value.isVector3) {
					return value.clone();
				}
				
				// 处理普通对象 {x, y, z}
				if (value.x !== undefined && value.y !== undefined && value.z !== undefined) {
					return new THREE.Vector3(value.x, value.y, value.z);
				}
				
				// 处理数组 [x, y, z]
				if (Array.isArray(value) && value.length >= 3) {
					return new THREE.Vector3(value[0], value[1], value[2]);
				}
				
				return defaultValue.clone();
			}

			convertToEuler(value, defaultValue) {
				if (!value) {
					return defaultValue.clone();
				}
				
				if (value.isEuler) {
					return value.clone();
				}
				
				// 处理普通对象 {x, y, z}
				if (value.x !== undefined && value.y !== undefined && value.z !== undefined) {
					return new THREE.Euler(value.x, value.y, value.z);
				}
				
				// 处理数组 [x, y, z]
				if (Array.isArray(value) && value.length >= 3) {
					return new THREE.Euler(value[0], value[1], value[2]);
				}
				
				return defaultValue.clone();
			}

			convertToQuaternion(value, defaultValue) {
				if (!value) {
					return defaultValue.clone();
				}
				
				if (value.isQuaternion) {
					return value.clone();
				}
				
				// 处理普通对象 {x, y, z, w}
				if (value.x !== undefined && value.y !== undefined && value.z !== undefined && value.w !== undefined) {
					return new THREE.Quaternion(value.x, value.y, value.z, value.w);
				}
				
				// 处理数组 [x, y, z, w]
				if (Array.isArray(value) && value.length >= 4) {
					return new THREE.Quaternion(value[0], value[1], value[2], value[3]);
				}
				
				return defaultValue.clone();
			}

			vectorToArray(vector) {
				if (!vector) return [0, 0, 0];
				if (Array.isArray(vector)) return vector;
				if (vector.isVector3) return vector.toArray();
				if (vector.x !== undefined) return [vector.x, vector.y, vector.z];
				return [0, 0, 0];
			}

			eulerToArray(euler) {
				if (!euler) return [0, 0, 0];
				if (Array.isArray(euler)) return euler;
				if (euler.isEuler) return [euler.x, euler.y, euler.z];
				if (euler.x !== undefined) return [euler.x, euler.y, euler.z];
				return [0, 0, 0];
			}

			quaternionToArray(quaternion) {
				if (!quaternion) return [0, 0, 0, 1];
				if (Array.isArray(quaternion)) return quaternion;
				if (quaternion.isQuaternion) return [quaternion.x, quaternion.y, quaternion.z, quaternion.w];
				if (quaternion.x !== undefined) return [quaternion.x, quaternion.y, quaternion.z, quaternion.w];
				return [0, 0, 0, 1];
			}

			// 模型加载与处理
			ImportDiagnostics() {
				console.log("=== Scene Diagnostics ===");
				
				// Record current scene state
				const sceneState = {
					objects: {},
					cameras: {},
					lights: [],
					animationInfo: null
				};
				
				// Collect object overview
				console.group("Scene Object Overview:");
				
				const objectStats = {
					total: 0,
					types: {},
					visible: 0,
					groups: 0,
					meshes: 0,
					lines: 0,
					points: 0
				};
				
				this.scene.traverse(function(child) {
					objectStats.total++;
					
					// Count by type
					const type = child.type || "Unknown";
					objectStats.types[type] = (objectStats.types[type] || 0) + 1;
					
					// Count specific categories
					if (child.isGroup) objectStats.groups++;
					if (child.isMesh) objectStats.meshes++;
					if (child.isLine) objectStats.lines++;
					if (child.isPoints) objectStats.points++;
					if (child.visible) objectStats.visible++;
					
					// Store object information
					sceneState.objects[child.name || "unnamed_" + objectStats.total] = {
						type: type,
						visible: child.visible,
						position: child.position ? child.position.toArray().map(function(v) { return v.toFixed(2); }) : null,
						userDataKeys: child.userData ? Object.keys(child.userData) : []
					};
				});
				
				console.log("Total objects: " + objectStats.total);
				console.log("Visible objects: " + objectStats.visible);
				console.log("Groups: " + objectStats.groups);
				console.log("Meshes: " + objectStats.meshes);
				console.log("Lines: " + objectStats.lines);
				console.log("Points: " + objectStats.points);
				
				// Display type distribution
				console.group("Object type distribution:");
				for (var type in objectStats.types) {
					if (objectStats.types.hasOwnProperty(type)) {
						console.log(type + ": " + objectStats.types[type]);
					}
				}
				console.groupEnd();
				
				console.groupEnd(); // Scene Object Overview group
				
				// Camera State group
				const cameraCounts = {
					default: this.state.cameras.default ? this.state.cameras.default.length : 0,
					custom: this.state.cameras.custom ? this.state.cameras.custom.length : 0,
					scene: this.state.cameras.scene ? this.state.cameras.scene.length : 0
				};
				
				const totalCameras = cameraCounts.default + cameraCounts.custom + cameraCounts.scene;
				console.group("Camera State (" + totalCameras + " cameras):");
				
				// Collect all cameras from all categories
				const allCameras = [];
				if (this.state.cameras.default) allCameras.push.apply(allCameras, this.state.cameras.default);
				if (this.state.cameras.custom) allCameras.push.apply(allCameras, this.state.cameras.custom);
				if (this.state.cameras.scene) allCameras.push.apply(allCameras, this.state.cameras.scene);
				
				// Analyze default cameras
				console.group("Default Cameras (" + cameraCounts.default + " cameras):");
				if (cameraCounts.default > 0 && this.state.cameras.default) {
					this.state.cameras.default.forEach(function(cam) {
						console.group("Camera: " + cam.name);
						console.log("Type: " + (cam.userData.cameraType || "default"));
						console.log("Position: [" + cam.position.x.toFixed(2) + ", " + cam.position.y.toFixed(2) + ", " + cam.position.z.toFixed(2) + "]");
						console.log("Rotation(degrees): [" + (cam.rotation.x * 180/Math.PI).toFixed(2) + ", " + (cam.rotation.y * 180/Math.PI).toFixed(2) + ", " + (cam.rotation.z * 180/Math.PI).toFixed(2) + "]");
						console.log("Projection type: " + (cam.isOrthographicCamera ? "Orthographic" : "Perspective"));
						if (cam.userData.targetPosition) {
							console.log("Target position: [" + cam.userData.targetPosition.x.toFixed(2) + ", " + cam.userData.targetPosition.y.toFixed(2) + ", " + cam.userData.targetPosition.z.toFixed(2) + "]");
						}
						console.groupEnd();
					}.bind(this));
				} else {
					console.log("No default cameras");
				}
				console.groupEnd(); // Default Cameras group
				
				// Analyze custom cameras
				console.group("Custom Cameras (" + cameraCounts.custom + " cameras):");
				if (cameraCounts.custom > 0 && this.state.cameras.custom) {
					this.state.cameras.custom.forEach(function(cam) {
						console.group("Camera: " + cam.name);
						console.log("Type: " + (cam.userData.cameraType || "custom"));
						console.log("Position: [" + cam.position.x.toFixed(2) + ", " + cam.position.y.toFixed(2) + ", " + cam.position.z.toFixed(2) + "]");
						console.log("Rotation(degrees): [" + (cam.rotation.x * 180/Math.PI).toFixed(2) + ", " + (cam.rotation.y * 180/Math.PI).toFixed(2) + ", " + (cam.rotation.z * 180/Math.PI).toFixed(2) + "]");
						console.log("Projection type: " + (cam.isOrthographicCamera ? "Orthographic" : "Perspective"));
						if (cam.userData.targetPosition) {
							console.log("Target position: [" + cam.userData.targetPosition.x.toFixed(2) + ", " + cam.userData.targetPosition.y.toFixed(2) + ", " + cam.userData.targetPosition.z.toFixed(2) + "]");
						}
						if (cam.userData.animationKeyframes && cam.userData.animationKeyframes.length > 0) {
							console.log("Animation keyframes (" + cam.userData.animationKeyframes.length + " frames):");
						} else {
							console.log("Animation keyframes: None");
						}
						console.groupEnd();
					}.bind(this));
				} else {
					console.log("No custom cameras");
				}
				console.groupEnd(); // Custom Cameras group
				
				// Analyze scene cameras
				console.group("Scene Cameras (" + cameraCounts.scene + " cameras):");
				if (cameraCounts.scene > 0 && this.state.cameras.scene) {
					this.state.cameras.scene.forEach(function(cam) {
						console.group("Camera: " + cam.name);
						console.log("Type: " + (cam.userData.cameraType || "scene"));
						console.log("Position: [" + cam.position.x.toFixed(2) + ", " + cam.position.y.toFixed(2) + ", " + cam.position.z.toFixed(2) + "]");
						console.log("Rotation(degrees): [" + (cam.rotation.x * 180/Math.PI).toFixed(2) + ", " + (cam.rotation.y * 180/Math.PI).toFixed(2) + ", " + (cam.rotation.z * 180/Math.PI).toFixed(2) + "]");
						console.log("Projection type: " + (cam.isOrthographicCamera ? "Orthographic" : "Perspective"));
						if (cam.userData.targetPosition) {
							console.log("Target position: [" + cam.userData.targetPosition.x.toFixed(2) + ", " + cam.userData.targetPosition.y.toFixed(2) + ", " + cam.userData.targetPosition.z.toFixed(2) + "]");
						}
						if (cam.userData.animationKeyframes && cam.userData.animationKeyframes.length > 0) {
							console.log("Animation keyframes (" + cam.userData.animationKeyframes.length + " frames):");
						} else {
							console.log("Animation keyframes: None");
						}
						console.groupEnd();
					}.bind(this));
				} else {
					console.log("No scene cameras");
				}
				console.groupEnd(); // Scene Cameras group
				
				console.groupEnd(); // Camera State group
				
				// Light State group
				console.group("Light State:");
				
				// Get all lights in scene
				const allLights = [];
				this.scene.traverse(function(child) {
					if (child.isLight) {
						allLights.push(child);
					}
				});
				
				// Check if we have default and scene lights in state
				const hasLightClassification = this.state.lights && this.state.lights.default && this.state.lights.scene;
				
				// Analyze default lights
				if (hasLightClassification) {
					console.group("Default Lights (" + this.state.lights.default.length + " lights):");
					this.state.lights.default.forEach(function(light, index) {
						console.group("Light " + index + ": " + light.name);
						console.log("Type: " + light.type);
						console.log("Position: [" + light.position.x.toFixed(2) + ", " + light.position.y.toFixed(2) + ", " + light.position.z.toFixed(2) + "]");
						console.log("Color: " + light.color.getHexString());
						console.log("Intensity: " + light.intensity.toFixed(2));
						console.groupEnd();
					});
					console.groupEnd(); // Default Lights group
				}
				
				// Analyze scene lights
				console.group("Scene Lights (" + (hasLightClassification ? this.state.lights.scene.length : allLights.length) + " lights):");
				if (hasLightClassification) {
					this.state.lights.scene.forEach(function(light, index) {
						console.group("Light " + index + ": " + light.name);
						console.log("Type: " + light.type);
						console.log("Position: [" + light.position.x.toFixed(2) + ", " + light.position.y.toFixed(2) + ", " + light.position.z.toFixed(2) + "]");
						console.log("Color: " + light.color.getHexString());
						console.log("Intensity: " + light.intensity.toFixed(2));
						console.groupEnd();
					});
				} else {
					allLights.forEach(function(light, index) {
						console.group("Light " + index + ": " + light.name);
						console.log("Type: " + light.type);
						console.log("Position: [" + light.position.x.toFixed(2) + ", " + light.position.y.toFixed(2) + ", " + light.position.z.toFixed(2) + "]");
						console.log("Color: " + light.color.getHexString());
						console.log("Intensity: " + light.intensity.toFixed(2));
						console.groupEnd();
					});
					console.log("Note: All lights are treated as Scene Lights (no classification in state).");
				}
				console.groupEnd(); // Scene Lights group
				
				console.log("Total light count: " + (hasLightClassification ? (this.state.lights.default.length + this.state.lights.scene.length) : allLights.length));
				console.groupEnd(); // Light State group
				
				// Animation information
				console.group("Animation Information:");
				
				let animationClipCount = 0;
				let animationSummary = { hasAnimations: false, clips: [] };
				
				if (this.state.currentAnimations && this.state.currentAnimations.length > 0) {
					animationClipCount = this.state.currentAnimations.length;
					console.log("Animation clip count: " + animationClipCount);
					
					this.state.currentAnimations.forEach(function(anim, index) {
						console.group("Animation clip " + index + ": " + anim.name);
						console.log("Duration: " + anim.duration.toFixed(2) + " seconds");
						console.log("Track count: " + anim.tracks.length);
						console.log("FPS: " + this.state.playback.fps);
						console.log("Total frames: " + this.state.playback.totalFrames);
						console.groupEnd();
						
						// Add to animation summary
						animationSummary.clips.push({
							name: anim.name,
							duration: anim.duration,
							tracks: anim.tracks.length
						});
					}.bind(this));
					
					animationSummary.hasAnimations = true;
				} else {
					console.log("Animation clips: None");
				}
				
				console.groupEnd(); // Animation Information group
				
				// Show summary message
				console.log("=== Scene Summary ===");
				console.log("Objects: " + objectStats.total + " (Visible: " + objectStats.visible + ")");
				console.log("Cameras: " + totalCameras + " (Default: " + cameraCounts.default + ", Custom: " + cameraCounts.custom + ", Scene: " + cameraCounts.scene + ")");
				console.log("Lights: " + (hasLightClassification ? (this.state.lights.default.length + this.state.lights.scene.length) : allLights.length) + (hasLightClassification ? " (Default: " + this.state.lights.default.length + ", Scene: " + this.state.lights.scene.length + ")" : ""));
				console.log("Animations: " + animationClipCount + " clip(s)");
				this.showMessage("Please check the console for detailed diagnostics.");
				
				// Output JSON state (simplified version)
				console.log("=== Scene State JSON (Simplified) ===");
				
				// Create simplified JSON state
				const simplifiedState = {
					timestamp: new Date().toISOString(),
					objectSummary: {
						total: objectStats.total,
						visible: objectStats.visible,
						byType: objectStats.types,
						byCategory: {
							groups: objectStats.groups,
							meshes: objectStats.meshes,
							lines: objectStats.lines,
							points: objectStats.points
						}
					},
					cameras: {},
					lights: {
						default: [],
						scene: []
					},
					animation: {
						hasAnimations: animationSummary.hasAnimations,
						clipCount: animationClipCount,
						clips: animationSummary.clips,
						currentFrame: this.state.playback ? Math.floor(this.state.playback.currentFrame) : 0,
						totalFrames: this.state.playback ? this.state.playback.totalFrames : 0,
						fps: this.state.playback ? this.state.playback.fps : 0
					},
					cameraSummary: {
						currentType: this.state.cameras.currentType,
						activeCamera: this.camera ? this.camera.name : null,
						counts: cameraCounts
					}
				};
				
				// Record key information for each camera
				allCameras.forEach(function(cam) {
					simplifiedState.cameras[cam.name] = {
						type: cam.userData.cameraType || "unknown",
						position: cam.position.toArray().map(function(v) { return v.toFixed(2); }),
						rotation: cam.rotation.toArray().map(function(v) { return (v * 180/Math.PI).toFixed(2); }),
						hasAnimation: cam.userData.animationKeyframes && cam.userData.animationKeyframes.length > 0,
						animationFrames: cam.userData.animationKeyframes ? cam.userData.animationKeyframes.length : 0
					};
				});
				
				// Record key information for each light
				if (hasLightClassification) {
					// Record default lights
					this.state.lights.default.forEach(function(light, index) {
						simplifiedState.lights.default.push({
							name: light.name || "default_light_" + index,
							type: light.type,
							position: [light.position.x.toFixed(2), light.position.y.toFixed(2), light.position.z.toFixed(2)],
							color: light.color.getHexString(),
							intensity: light.intensity.toFixed(2)
						});
					});
					
					// Record scene lights
					this.state.lights.scene.forEach(function(light, index) {
						simplifiedState.lights.scene.push({
							name: light.name || "scene_light_" + index,
							type: light.type,
							position: [light.position.x.toFixed(2), light.position.y.toFixed(2), light.position.z.toFixed(2)],
							color: light.color.getHexString(),
							intensity: light.intensity.toFixed(2)
						});
					});
				} else {
					// Record all lights as scene lights
					allLights.forEach(function(light, index) {
						simplifiedState.lights.scene.push({
							name: light.name || "light_" + index,
							type: light.type,
							position: [light.position.x.toFixed(2), light.position.y.toFixed(2), light.position.z.toFixed(2)],
							color: light.color.getHexString(),
							intensity: light.intensity.toFixed(2)
						});
					});
				}
				
				console.log(JSON.stringify(simplifiedState, null, 2));
				
				console.log("=== Export/Reimport Diagnostics Complete ===");
			}

			handleImportFile(event) {
				const file = event.target.files[0];
				if (file) {
					const fileName = file.name; const format = this.detectFormat(fileName);
					
					const reader = new FileReader();
					reader.onload = (e) => this.load3DDataFromBuffer(e.target.result, fileName, format);
					if (['bin', 'fbx', 'glb', 'ply'].includes(format)) {
						reader.readAsArrayBuffer(file);
					} else {
						reader.readAsText(file);
					}
				}
				event.target.value = '';
			}

			async load3DDataFromBuffer(buffer, filename, format) {
				await this.process3DModelLoading(filename, format, async () => {
					if (format === 'bin') this.parseSMPL(buffer);
					else if (format === 'glb') await this.loadGLBFromBuffer(buffer);
					else if (format === 'fbx') await this.loadFBXFromBuffer(buffer);
					else if (format === 'obj') await this.loadOBJFromText(buffer);
					else if (format === 'ply') await this.loadPLYFromBuffer(buffer);
					else throw new Error("Unsupported format: " + format);
				});
			}

			async load3DData(filename, formatHint = 'auto') {
				if (!filename) throw new Error("No filename provided");
				const format = formatHint === 'auto' ? this.detectFormat(filename) : formatHint;
				
				await this.process3DModelLoading(filename, format, async () => {
					if (format === 'bin') await this.loadSMPLBin(filename);
					else if (format === 'glb') await this.loadGLB(filename);
					else if (format === 'fbx') await this.loadFBX(filename);
					else if (format === 'obj') await this.loadOBJ(filename);
					else if (format === 'ply') await this.loadPLY(filename);
					else throw new Error("Unsupported format: " + format);
				});
			}

			detectFormat(filename) { 
				const ext = filename.split('.').pop().toLowerCase(); 
				const map = { 
					'glb': 'glb', 
					'fbx': 'fbx', 
					'obj': 'obj', 
					'ply': 'ply', 
					'bin': 'bin'
				}; 
				return map[ext] || 'glb'; 
			}

			async process3DModelLoading(filename, format, loadOperation) {
				if (this.state.loading) return;
				this.state.loading = true; 
				this.showMessage("Loading 3D data...", -1);
				
				this.pause();
				this.state.playback.currentFrame = 0;
				this.state.playback.totalFrames = 0;
				
				try {
					this.state.currentFormat = format;
					this.state.currentFileData = { filename, format };
					
					await this.cleanupPreviousModel();
					await loadOperation();
					
					this.postModelLoading();
					
				} catch (e) { 
					this.showMessage("Error: " + e.message, 5000); 
					throw e;
				} finally { 
					this.state.loading = false; 
					if (!this._messageTimer) {
						this.dom.loading.style.display = 'none'; 
					}
				}
			}

			postModelLoading() {
				this.applyMaterialMode();
				this.updateVisuals(0);
				this.updateTimeSleder();
				this.updateInfoDisplay();
				
				if (!this.camera.userData.rollAngle || !this.camera.userData.upVector) {
					this.camera.up.set(0, 1, 0);
				} else {
					this.camera.up.copy(this.camera.userData.upVector);
				}
				
				// 初始化动画包围盒数据系统
				this.initAnimationBBoxData();
				
				// 从 animationBBoxData 中获取第0帧数据来设置原有变量
				if (this.state.animationBBoxData.isInitialized) {
					// 获取当前帧（第0帧）数据
					const frame0Data = this.getBBoxForCurrentFrame();
					
					if (frame0Data && !frame0Data.isEmpty) {
						this.state.sceneBBox = frame0Data.box;
						this.state.sceneCenter = frame0Data.center;
					} else {
						// 确保获取场景包围盒
						this.state.sceneBBox = this.getBBox();
						if (this.state.sceneBBox && !this.state.sceneBBox.isEmpty()) {
								this.state.sceneBBox.getCenter(this.state.sceneCenter);
						}
					}
				}
				
				this.adjustDefaultDirLightForScene();
				
				this.showMessage("Model loaded successfully", 1000);
				
				setTimeout(() => {
					if (typeof lil !== 'undefined' && lil.GUI) {
						this.createMaterialGUI();
					}
				}, 200);
				
				setTimeout(() => this.onWindowResize(), 100);
			}

			async loadSMPLBin(filename) {
				const res = await fetch('/adv3dviewer_jk?filename=' + filename);
				const buf = await res.arrayBuffer();
				this.parseSMPL(buf);
			}

			parseSMPL(buffer) {
				const dv = new DataView(buffer);
				let offset = 4;
				
				const numFrames = dv.getUint32(offset, true);
				offset += 4;
				const numVerts = dv.getUint32(offset, true);
				offset += 4;
				const numFaces = dv.getUint32(offset, true);
				offset += 4;
				this.state.playback.fps = dv.getFloat32(offset, true);
				offset += 4;
				
				const verts = new Float32Array(buffer, offset, numFrames * numVerts * 3);
				offset += numFrames * numVerts * 3 * 4;
				
				const faces = new Uint32Array(buffer, offset, numFaces * 3);
				
				this.state.smplData = {
					vertices: verts,
					faces: faces,
					numFrames, numVerts
				};
				
				const geo = new THREE.BufferGeometry();
				geo.setAttribute('position', new THREE.BufferAttribute(verts.subarray(0, numVerts*3), 3));
				geo.setIndex(new THREE.BufferAttribute(faces, 1));
				geo.computeVertexNormals();
				
				const mat = this.createDefaultMaterial();
				this.state.smplMesh = new THREE.Mesh(geo, mat);
				
				// 根据当前阴影设置启用阴影
				this.state.smplMesh.castShadow = this.state.lights.shadowsEnabled;
				this.state.smplMesh.receiveShadow = this.state.lights.shadowsEnabled;
				
				this.scene.add(this.state.smplMesh);
				this.state.currentModel = this.state.smplMesh;
				this.state.playback.totalFrames = numFrames;
			}

			async loadGLB(filename) {
				return new Promise((resolve, reject) => {
					this.loaders.gltf.load('/adv3dviewer_jk?filename=' + filename, (gltf) => {
						this.processLoadedGLB(gltf);
						resolve();
					}, 
					// 添加进度回调以处理纹理加载
					(xhr) => {
						if (xhr.lengthComputable) {
							const percentComplete = (xhr.loaded / xhr.total) * 100;
							if (percentComplete < 100) {
								this.showMessage("Loading model: " + percentComplete.toFixed(2) + "%", -1);
							}
						}
					}, 
					reject);
				});
			}

			async loadGLBFromBuffer(buffer) {
				return new Promise((resolve, reject) => {
					this.loaders.gltf.parse(buffer, '', (gltf) => {
						this.processLoadedGLB(gltf);
						resolve();
					}, reject);
				});
			}

			processLoadedGLB(gltf) {
				this.state.currentFormat = 'glb';
				
				const cameras = [];
				gltf.scene.traverse(child => {
					if (child.isCamera) {
						cameras.push(child);
					}
					
					if (child.isMesh) {
						if (!child.material) {
							child.material = this.createDefaultMaterial();
							child.userData.autoCreatedMaterial = true;
						} else {
							child.userData.autoCreatedMaterial = false;
						}
						
						// 根据当前阴影设置启用阴影
						child.castShadow = this.state.lights.shadowsEnabled;
						child.receiveShadow = this.state.lights.shadowsEnabled;
					}
				});
				
				this.scene.add(gltf.scene); 
				this.state.currentModel = gltf.scene;
				
				// 在动画处理之前保存材质和纹理
				this.saveOriginalMaterials(gltf.scene);
				
				if (gltf.animations && gltf.animations.length > 0) {
					this.state.currentAnimations = gltf.animations; 
					this.state.currentMixer = new THREE.AnimationMixer(gltf.scene);
					
					gltf.animations.forEach((clip) => {
						const action = this.state.currentMixer.clipAction(clip); 
						action.play();
					});
					
					const clip = gltf.animations[0]; 
					this.state.playback.totalFrames = Math.ceil(clip.duration * this.state.playback.fps); 
					
				} else { 
					this.state.playback.totalFrames = 1; 
				}
				
				// 检查是否为已导出的文件，并跳过预处理
				const sceneDetection = this.detectExportedScene(gltf.scene);
				const isExportedScene = sceneDetection.isExported;
				const nestedLevel = sceneDetection.nestedLevel;
				
				// 检查是否包含导出的相机数据
				const hasExportedCameras = gltf.scene.userData && gltf.scene.userData.sceneCameras;
				const hasExportedCustomCameras = gltf.scene.userData && gltf.scene.userData.customCameras;
				
				// 如果检测到是已导出的场景且嵌套层级大于0，需要展平场景
				if (isExportedScene && nestedLevel > 0) {
					// 只处理嵌套的ImportedScene节点，不移除相机节点
					if (sceneDetection.baseScene) {
						const baseScene = sceneDetection.baseScene;
						const nodesToReparent = [];
						
						// 查找所有需要重新父级分配的节点
						baseScene.traverse(child => {
							// 跳过相机节点和baseScene本身
							if (child === baseScene || child.isCamera) return;
							
							// 如果是嵌套的ImportedScene节点，将其子节点重新分配到baseScene
							if (child.name === 'ImportedScene' || 
								(child.userData && child.userData.name === 'ImportedScene')) {
								child.children.forEach(grandChild => {
									if (!nodesToReparent.includes(grandChild)) {
										nodesToReparent.push(grandChild);
									}
								});
							} else {
								// 其他节点保持不变
								if (!nodesToReparent.includes(child)) {
									nodesToReparent.push(child);
								}
							}
						});
						
						// 清空baseScene，重新添加节点
						while (baseScene.children.length > 0) {
							baseScene.remove(baseScene.children[0]);
						}
						
						// 重新添加所有节点到baseScene
						nodesToReparent.forEach(node => {
							if (node.parent) {
								node.parent.remove(node);
							}
							baseScene.add(node);
						});
					}
				}
				
				// 如果检测到是已导出的场景，确保正确的节点层级
				if (isExportedScene) {
					// 标记整个场景为已导出数据
					gltf.scene.traverse(child => {
						if (child.isCamera) {
							child.userData.isExportedData = true;
							child.userData.skipPreprocessing = true;
						}
						
						// 标记模型节点为已导出
						if (child.isMesh || child.isGroup) {
							child.userData.isExportedData = true;
						}
					});
				}
				
				// 从场景的 userData 中恢复自定义相机数据
				if (gltf.scene.userData && gltf.scene.userData.customCameras) {
					const customCamerasData = gltf.scene.userData.customCameras;
					
					// 遍历场景，查找自定义相机并恢复数据
					gltf.scene.traverse(child => {
						if (child.isCamera && child.name && child.name.startsWith('CustomCamJK_')) {
							const cameraData = customCamerasData[child.name];
							if (cameraData) {
								
								// 恢复基本属性
								child.userData.controlsTarget = new THREE.Vector3().fromArray(cameraData.controlsTarget);
								child.userData.rollAngle = cameraData.rollAngle || 0;
								child.userData.upVector = new THREE.Vector3().fromArray(cameraData.upVector);
								child.userData.initialDistance = cameraData.initialDistance || 5;
								child.userData.actualZoomFactor = cameraData.actualZoomFactor || 1.0;
								child.userData.viewHeight = cameraData.viewHeight;
								
								// 恢复关键帧数据
								if (cameraData.keyframes && cameraData.keyframes.length > 0) {
									child.userData.keyframes = cameraData.keyframes.map(kfData => {
										const keyframe = {
											frame: kfData.frame,
											position: new THREE.Vector3().fromArray(kfData.position),
											fov: kfData.fov,
											controlsTarget: new THREE.Vector3().fromArray(kfData.controlsTarget),
											roll: kfData.roll,
											isOrthographic: kfData.isOrthographic
										};
										
										// 处理旋转数据
										if (kfData.quaternion) {
											keyframe.quaternion = new THREE.Quaternion(
												kfData.quaternion[0],
												kfData.quaternion[1],
												kfData.quaternion[2],
												kfData.quaternion[3]
											);
											keyframe.rotation = new THREE.Euler().setFromQuaternion(keyframe.quaternion);
										} else if (kfData.rotation) {
											keyframe.rotation = new THREE.Euler(
												kfData.rotation[0],
												kfData.rotation[1],
												kfData.rotation[2]
											);
										}
										
										return keyframe;
									});
									
									// 对关键帧按帧号排序
									child.userData.keyframes.sort((a, b) => a.frame - b.frame);
								} else {
									// 如果没有关键帧数据，创建空数组
									child.userData.keyframes = [];
								}
								
								// 标记为已导出的自定义相机
								child.userData.isExportedData = true;
								child.userData.skipPreprocessing = true;
							}
						}
					});
				}
				
				// 检查场景中是否有SMPL帧网格
				let smplFrameCount = 0;
				gltf.scene.traverse(child => {
					if (child.isMesh && child.userData && child.userData.isSMPLFrame) {
						smplFrameCount++;
					}
				});
				
				// 如果检测到SMPL帧网格，设置smplData
				if (smplFrameCount > 0) {
					this.state.smplData = {
						numFrames: smplFrameCount
					};
					this.state.playback.totalFrames = smplFrameCount;
				}
				
				// 根据是否有导出数据决定是否跳过预处理
				if (isExportedScene || hasExportedCameras || hasExportedCustomCameras) {
					// 有导出数据：跳过预处理，直接恢复场景相机
					this.restoreExportedSceneCameras(gltf.scene);
					
					// 对于已导出的场景，还需要识别自定义相机
					this.identifyCustomCameras(gltf.scene);
				} else {
					// 无导出数据：正常进行预处理
					this.processSceneCameras(gltf.scene);
					this.identifyCustomCameras(gltf.scene);
				}
				
				// 记录场景的原始名称（用于导出时避免重复嵌套）
				if (!isExportedScene) {
					gltf.scene.userData.originalSceneName = gltf.scene.name || 'UnknownScene';
				}
				
				this.processSceneLights(gltf.scene);
				
				// 检查是否有SMPL可见性动画数据
				if (gltf.scene.userData && gltf.scene.userData.smplAnimation && gltf.scene.userData.smplAnimation.visibility) {
					this.processSMPLVisibilityAnimation(gltf.scene);
					const currentFrame = Math.floor(this.state.playback.currentFrame);
					this.updateSMPLVisibility(currentFrame);
				}
			}

			async loadFBX(filename) {
			  const res = await fetch('/adv3dviewer_jk?filename=' + filename);
			  if (!res.ok) throw new Error('Network response error');
			  const buf = await res.arrayBuffer();
			  await this.loadFBXFromBuffer(buf);
			}

			async loadFBXFromBuffer(buffer) {
				return new Promise((resolve, reject) => {
					try {
						const object = this.loaders.fbx.parse(buffer, '');
						this.processLoadedFBX(object);
						resolve();
					} catch (error) {
						if (error.message && (error.message.includes('curveNodesMap') || error.message.includes('curves'))) {
							reject(new Error("FBX import failed: Three.js FBXLoader does not support camera/light property animations; remove property keyframes and re-export."));
						} else {
							reject(error);
						}
					}
				});
			}

			processLoadedFBX(object) {
				this.state.currentFormat = 'fbx';
				
				this.scene.add(object); 
				this.state.currentModel = object;
				
				// 先保存原始材质和纹理
				this.saveOriginalMaterials(object);
				
				object.traverse(child => {
					if (child.isMesh) {
						if (!child.material) {
							child.material = this.createDefaultMaterial();
							child.userData.autoCreatedMaterial = true;
						} else {
							child.userData.autoCreatedMaterial = false;
						}
						
						// 确保几何体有法线
						if (child.geometry && !child.geometry.attributes.normal) {
							child.geometry.computeVertexNormals();
						}
						
						// 根据当前阴影设置启用阴影
						child.castShadow = this.state.lights.shadowsEnabled;
						child.receiveShadow = this.state.lights.shadowsEnabled;
					}
				});
				
				if (object.animations && object.animations.length > 0) {
					this.state.currentAnimations = object.animations; 
					this.state.currentMixer = new THREE.AnimationMixer(object);
					
					object.animations.forEach((clip) => {
						const action = this.state.currentMixer.clipAction(clip); 
						action.play();
					});
					
					const clip = object.animations[0]; 
					this.state.playback.totalFrames = Math.ceil(clip.duration * this.state.playback.fps); 
				} else { 
					this.state.playback.totalFrames = 1; 
				}
				
				this.processSceneCameras(object);
				this.identifyCustomCameras(object);
				this.processSceneLights(object);
			}

			async loadOBJ(filename) {
				return new Promise(async (resolve, reject) => {
					try {
						const baseName = filename.replace(/\.obj$/i, '');
						const objUrl = '/adv3dviewer_jk?filename=' + filename;
						
						// 先尝试获取MTL文件
						let mtlData = null;
						let materials = null;
						
						try {
							const mtlUrl = '/adv3dviewer_jk?filename=' + baseName + '.mtl';
							const mtlResponse = await fetch(mtlUrl);
							if (mtlResponse.ok) {
								const mtlText = await mtlResponse.text();
							  
								// 解析MTL文件，获取纹理路径
								const mtlLoader = new MTLLoader();
							  
								// 设置纹理路径为相对路径
								mtlLoader.setTexturePath('/adv3dviewer_jk/');
							  
								// 解析MTL文本
								materials = mtlLoader.parse(mtlText, '');
							  
								if (materials) {
									materials.preload();
									console.log("MTL materials loaded successfully");
								}
							}
						} catch (mtlError) {
							console.log("No MTL file found or error loading MTL, using default materials");
						}
						
						// 加载OBJ文件
						const objResponse = await fetch(objUrl);
						if (!objResponse.ok) {
							throw new Error("Failed to load OBJ file: " + objResponse.status);
						}
						
						const objText = await objResponse.text();
						
						// 使用合适的加载器
						const objLoader = new OBJLoader();
						if (materials) {
							objLoader.setMaterials(materials);
						}
						
						const object = objLoader.parse(objText);
						
						// 处理加载的OBJ对象
						this.processLoadedOBJ(object, materials, filename);
						resolve();
						
					} catch (error) {
						console.log("Error loading OBJ: " + error.message);
					  reject(error);
					}
				});
			}

			async loadOBJFromText(text) {
				return new Promise((resolve, reject) => {
					try {
						const object = this.loaders.obj.parse(text);
						this.processLoadedOBJ(object, null, "imported.obj");
						resolve();
					} catch (error) {
						reject(error);
					}
				});
			}

			processLoadedOBJ(object, materials, filename) {
				this.scene.add(object);
				this.state.currentModel = object;
				this.state.currentFormat = 'obj';
				
				// 保存材质和纹理
				this.saveOriginalMaterials(object);
				
				// 如果没有材质，创建默认材质
				let hasMaterials = false;
				object.traverse(child => {
					if (child.isMesh && child.material) {
						hasMaterials = true;
					}
				});
				
				if (!hasMaterials) {
					// 创建默认材质
					const defaultMaterial = this.createDefaultMaterial();
					
					object.traverse(child => {
						if (child.isMesh) {
							child.material = defaultMaterial;
							child.userData.autoCreatedMaterial = true;
						} else {
							child.userData.autoCreatedMaterial = false;
						}
						
						// 根据当前阴影设置启用阴影
						child.castShadow = this.state.lights.shadowsEnabled;
						child.receiveShadow = this.state.lights.shadowsEnabled;
					});
					
					// 重新保存材质
					this.saveOriginalMaterials(object);
				}
				
				// 确保几何体有法线
				object.traverse(child => {
					if (child.isMesh && child.geometry && !child.geometry.attributes.normal) {
						child.geometry.computeVertexNormals();
					}
				});
				
				this.state.playback.totalFrames = 1;
				
				// 输出加载信息
				console.log("OBJ loaded: " + filename);
				if (materials) {
					console.log("MTL materials applied");
				}
				if (this.state.originalTextures.size > 0) {
					console.log("Found " + this.state.originalTextures.size + " textures in OBJ");
				}
			}

			async loadPLY(filename) {
				const res = await fetch('/adv3dviewer_jk?filename=' + filename);
				if(!res.ok) throw new Error('Network error');
				const buf = await res.arrayBuffer();
				await this.loadPLYFromBuffer(buf);
			}

			async loadPLYFromBuffer(buffer) {
				return new Promise((resolve, reject) => {
					try { 
						const geometry = this.loaders.ply.parse(buffer);
						
						// 检查顶点颜色属性
						const hasVertexColors = geometry.attributes.color !== undefined;
						const hasNormals = geometry.attributes.normal !== undefined;
						
						// 如果没有法线，计算顶点法线（对于网格）
						if (!hasNormals) {
							geometry.computeVertexNormals();
						}
						
						// 检查几何体类型（点云或网格）
						let isPointCloud = false;
						if (geometry.getIndex() === null || geometry.getIndex().count === 0) {
							// 没有索引，可能是点云
							isPointCloud = true;
						}
						
						let material;
						let mesh;
						
						if (isPointCloud) {
							// 点云渲染
							const pointMaterial = hasVertexColors
								? new THREE.PointsMaterial({
									size: 0.005,
									vertexColors: true,
									sizeAttenuation: true
								})
								: new THREE.PointsMaterial({
									size: 0.005,
									color: 0xcccccc,
									sizeAttenuation: true
								});
							
							mesh = new THREE.Points(geometry, pointMaterial);
							this.state.useVertexColors = hasVertexColors;
						
						} else {
							// 网格渲染
							if (hasVertexColors) {
								material = new THREE.MeshStandardMaterial({
									vertexColors: true,
									roughness: 1,
									metalness: 0,
									side: THREE.DoubleSide,
									flatShading: false
								});
								this.state.useVertexColors = true;
							} else {
								material = this.createDefaultMaterial();
								this.state.useVertexColors = false;
							}
							
							mesh = new THREE.Mesh(geometry, material);
						}
						
						// 保存材质
						this.state.originalMaterials.set(mesh, mesh.material);
						
						this.scene.add(mesh);
						this.state.currentModel = mesh;
						this.state.currentFormat = 'ply';
						this.state.playback.totalFrames = 1;
						
						// 输出PLY信息
						console.log("PLY loaded: " + (isPointCloud ? "Point Cloud" : "Mesh"));
						console.log("Vertex colors: " + (hasVertexColors ? "Yes" : "No"));
						console.log("Normals: " + (hasNormals ? "Original" : "Computed"));
						
						resolve();
					} catch (error) {
						console.log("Error loading PLY: " + error.message);
					  reject(error);
					}
				});
			}

			// 场景清理
			async cleanupPreviousModel() {
				// 1. 清理相机
				// 清理当前激活的自定义相机状态
				if (this.state.cameras.currentType === 'custom' && this.camera) {
					this.clearCameraAnimationData(this.camera);
					this.state.cameras.states.delete(this.camera.name);
				}
				
				// 清理自定义相机及其状态
				this.state.cameras.custom.forEach(cam => {
					this.clearCameraAnimationData(cam);
					this.scene.remove(cam);
					if (cam.userData.visualization) cam.userData.visualization.forEach(a => this.scene.remove(a));
					this.state.cameras.states.delete(cam.name);
				});
				this.state.cameras.custom = [];
				this.state.cameras.customCount = 0;
				
				// 清理场景相机及其状态缓存
				this.state.cameras.scene.forEach(cam => {
					if (cam.userData.visualization) cam.userData.visualization.forEach(a => this.scene.remove(a));
					this.scene.remove(cam);
					this.state.cameras.states.delete(cam.name);
				});
				this.state.cameras.scene = [];
				this.state.cameras.activeScene = null;
				
				// 防御性清理所有残留的场景相机状态
				for (const camName of Array.from(this.state.cameras.states.keys())) {
					const isDefault = this.state.cameras.default.some(c => c.name === camName);
					const isCustom = camName.startsWith('CustomCamJK_');
					if (!isDefault && !isCustom) {
						this.state.cameras.states.delete(camName);
					}
				}
				
				// 切换回默认相机
				if (this.state.cameras.currentType !== 'default' && this.state.cameras.default.length > 0) {
					this.switchToCamera(this.state.cameras.default[0]);
					this.dom.inputs.views.value = "User";
				}
				
				// 恢复默认相机的 near 和 far clip 值
				this.camera.near = 0.01;
				this.camera.far = 500;
				
				// 更新相机投影矩阵
				this.camera.updateProjectionMatrix();
				
				// 更新UI
				if (this.dom.inputs.near) {
					this.dom.inputs.near.value = this.camera.near.toFixed(2);
				}
				if (this.dom.inputs.far) {
					this.dom.inputs.far.value = this.camera.far.toFixed(2);
				}
				
				// 使用 calculateCameraRollAngle 计算当前的 roll 和 up 向量
				const rollResult = this.calculateCameraRollAngle(this.camera, this.controls.target);
				const rollAngle = rollResult.roll;
				const upVector = rollResult.upVector;
				
				// 更新相机的 userData
				this.camera.userData.rollAngle = rollAngle;
				this.camera.userData.upVector = upVector.clone();
				
				if (!this.camera.userData.rollAngle || !this.camera.userData.upVector) {
					this.camera.up.set(0, 1, 0);
				} else {
					this.camera.up.copy(this.camera.userData.upVector);
				}
				this.controls.update();
				
				// 同步 roll 输入框
				if (this.dom.inputs.rollAngle) {
					if (this.camera.userData.rollAngle !== undefined) {
						this.dom.inputs.rollAngle.value = this.camera.userData.rollAngle.toFixed(2);
					} else {
						this.dom.inputs.rollAngle.value = "0.00";
						this.camera.userData.rollAngle = 0;
					}
				}
				
				// 2. 清理场景灯光
				this.state.lights.scene.forEach(light => {
					if (light.userData.sphereVisualization) {
						this.scene.remove(light.userData.sphereVisualization);
						light.userData.sphereVisualization = null;
					};
					this.scene.remove(light);
				});
				this.state.lights.scene = [];
				
				// 重新启用默认灯光
				this.state.useSceneLight = true;
				this.state.lights.shadowsEnabled = true;
				this.toggleLightMode();
				this.toggleShadows();
				
				// 重置默认灯光到初始位置
				if (this.state.lights.dir) {
					this.state.lights.dir.position.set(50, 50, 50);
					this.state.lights.dir.target.position.set(0, 0, 0);
					
					// 重置阴影相机参数
					const shadowCamera = this.state.lights.dir.shadow.camera;
					shadowCamera.left = this.state.lights.shadowSettings.camera.left;
					shadowCamera.right = this.state.lights.shadowSettings.camera.right;
					shadowCamera.top = this.state.lights.shadowSettings.camera.top;
					shadowCamera.bottom = this.state.lights.shadowSettings.camera.bottom;
					shadowCamera.near = this.state.lights.shadowSettings.camera.near;
					shadowCamera.far = this.state.lights.shadowSettings.camera.far;
					shadowCamera.updateProjectionMatrix();
					
					// 重置阴影贴图分辨率
					this.state.lights.dir.castShadow = this.state.lights.shadowsEnabled;
					this.state.lights.dir.shadow.mapSize.width = this.state.lights.shadowSettings.mapSize;
					this.state.lights.dir.shadow.mapSize.height = this.state.lights.shadowSettings.mapSize;
					this.state.lights.dir.shadow.needsUpdate = true;
					
					// 更新灯光可视化位置
					if (this.state.lights.dir.userData.sphereVisualization) {
						this.state.lights.dir.userData.sphereVisualization.position.set(50, 50, 50);
					}
				}
				
				// 3. 清理场景模型
				if (this.state.currentModel) {
					this.scene.remove(this.state.currentModel);
					if (this.state.currentModel.isScene || this.state.currentModel.isObject3D) {
						this.state.currentModel.traverse(child => {
							if (child.geometry) child.geometry.dispose();
							if (child.material) {
								if (Array.isArray(child.material)) {
									child.material.forEach(m => m.dispose());
								} else {
									child.material.dispose();
								}
							}
						});
					}
					this.state.currentModel = null;
				}
				
				if (this.state.smplMesh) {
					this.scene.remove(this.state.smplMesh);
					if (this.state.smplMesh.geometry) {
						this.state.smplMesh.geometry.dispose()
					};
					if (this.state.smplMesh.material) {
						this.state.smplMesh.material.dispose()
					};
					this.state.smplMesh = null;
				}
				
				// 4. 清理动画
				if (this.state.currentMixer) {
					this.state.currentMixer.stopAllAction();
					if (this.state.currentModel) {
						this.state.currentMixer.uncacheRoot(this.state.currentModel);
					}
					this.state.currentMixer = null;
				}
				this.state.currentAnimations = [];
				this.state.smplData = null;
				
				// 5. 清理材质贴图
				// 重置材质模式为original
				const materialSelect = document.getElementById('material-mode-select');
				if (materialSelect) {
					materialSelect.value = 'original';
					this.state.materialMode = 'original';
					this.applyMaterialMode();
					this.updateBgColorPickerState('original');
				}
				
				// 清理材质纹理缓存
				this.state.originalMaterials.clear();
				this.disposeMaterialCache();
				this.disposeTextureCache();
				
				// 重置纹理相关状态
				this.state.useVertexColors = false;
				this.state.textureMapping = true;
				
				// 6. 重置核心状态
				this.state.cameras.currentType = 'default';
				this.state.cameras.activeScene = null;
				this.state.cameraAnim.keyframes = [];
				this.state.cameraAnim.isEnabled = false;
				this.state.autoAddKeyframeEnabled = false;
				this.hideMaterialGUI();
				this.controls.enabled = true;
				
				// 重置录制状态
				if (this.state.recording.isRecording) {
					this.state.recording.isRecording = false;
					this.dom.btns.record.classList.remove('recording');
				}
				
				this.updateViewsMenu();
			}

			async clearScene() {
				if (this.state.playback.isPlaying) this.pause();
				
				// 清理场景内容（包括场景相机及其状态）
				await this.cleanupPreviousModel();
				
				// 重置包围盒缓存
				this.state.sceneBBox = null;
				this.state.sceneCenter = new THREE.Vector3();
				this.resetSettings();
				
				// 清理动画包围盒数据
				this.state.animationBBoxData = {
					sampledFrames: new Map(),
					aggregated: {
						overallMin: null,
						overallMax: null,
						averageCenter: null,
						overallSize: null
					},
					cachedFrames: new Map(),
					sampleFrameNumbers: [],
					samplingInterval: 25,
					isInitialized: false,
					hasAnimation: false
				};
				
				// 重置场景数据
				this.state.currentFormat = null;
				this.state.currentFileData = null;
				this.state.playback.totalFrames = 0;
				
				// 更新UI
				/* this.updateTimeSleder();
				this.updateKeyframeCount();
				this.updateKeyframeButtonsState();
				this.updateCameraUIForMode(); */
				
				this.updateInfoDisplay();
			}

			clearCameraAnimationData(camera) {
				if (!camera || !camera.userData) return;
				
				// 清除所有动画相关数据
				delete camera.userData.keyframes;
				delete camera.userData.animationKeyframes;
				delete camera.userData.animationFov;
				delete camera.userData.animationRoll;
				delete camera.userData.extraAnimationData;
				delete camera.userData.serializedKeyframes;
				delete camera.userData.hasAnimation;
				delete camera.userData.animationClip;
				delete camera.userData.animationTracks;
				delete camera.userData.animationMixer;
			}

			disposeMaterialCache() {
				const specialMaterials = [
					this.state.materials.default,
					this.state.materials.wireframe,
					this.state.materials.normal,
					this.state.materials.depth,
					this.state.materials.lineart,
					this.state.materials.contour,
					this.state.materials.edge,
					this.state.materials.canny
				];
				
				specialMaterials.forEach(mat => {
					if (mat && mat.dispose) {
						mat.dispose();
					}
				});
				
				// 重置材质对象
				this.state.materials = {
					default: null,
					wireframe: null,
					normal: null,
					depth: null,
					lineart: null,
					contour: null,
					edge: null,
					canny: null
				};
			}

			disposeTextureCache() {
				// 1. 清理纹理缓存
				this.state.textureCache.forEach((texture, url) => {
					try {
						if (texture && texture.dispose) {
							texture.dispose();
						}
					} catch (error) {
						console.log("Error disposing texture: " + url);
					}
				});
				this.state.textureCache.clear();
			  
				// 2. 清理原始纹理引用（不清除原始纹理本身，因为它们属于材质）
				this.state.originalTextures.clear();
			}

			// 模型动画输出
			exportModel() {
				if (!this.state.currentModel && !this.state.smplMesh) { 
					this.showMessage("No model to export", 3000); 
					return; 
				}
				
				// 创建全新的导出场景，不再复用旧场景
				const exportScene = new THREE.Scene();
				exportScene.name = "ExportedScene";
				
				// 清除任何可能存在的旧数据
				exportScene.userData = {};
				
				const restoreInfo = [];
				
				const reparent = (obj) => {
					restoreInfo.push({ 
						object: obj, 
						parent: obj.parent, 
						visible: obj.visible 
					});
					obj.visible = true;
					
					// 检查对象是否已经在导出场景中
					if (!exportScene.children.includes(obj)) {
						exportScene.add(obj);
					}
				};
				
				// 创建新的ImportedScene节点
				const importedSceneNode = new THREE.Group();
				importedSceneNode.name = 'ImportedScene';
				importedSceneNode.userData = {
					name: 'ImportedScene',
					isContainer: true,
					originalName: this.state.currentModel ? (this.state.currentModel.name || 'UnknownScene') : 'UnknownScene'
				};
				exportScene.add(importedSceneNode);
				
				// 用于跟踪已经处理的动画剪辑，避免重复
				const processedAnimationClips = new Set();
				const allAnimations = [];
				
				// 处理SMPL模型 - 使用独立的导出函数
				if (this.state.smplData && this.state.smplData.vertices) {
					const smplExportResult = this.exportSMPLAnimation(
						this.state.smplData,
						// SMPL这里不能使用importedSceneNode
						exportScene,
						allAnimations
					);
					
				} else if (this.state.smplData && this.state.smplData.smplFrames) {
					// 直接添加所有网格到ImportedScene
					if (this.state.smplData.allMeshes) {
						this.state.smplData.allMeshes.forEach(mesh => {
							if (!importedSceneNode.children.includes(mesh)) {
								reparent(mesh);
								importedSceneNode.add(mesh);
							}
						});
					}
					
					// 如果有可见性数据，保存到场景
					if (this.state.smplData.visibilityData) {
						exportScene.userData.smplAnimation = {
							visibility: this.state.smplData.visibilityData
						};
					}
				} else {
					// 普通模型：保持原始层级结构
					if (this.state.currentModel) {
						// 检查当前模型是否为已导出的场景
						const modelDetection = this.detectExportedScene(this.state.currentModel);
						
						if (modelDetection && modelDetection.isExported && modelDetection.baseScene) {
							// 如果是已导出的场景，提取baseScene的内容
							modelDetection.baseScene.children.forEach(child => {
								if (!importedSceneNode.children.includes(child)) {
									reparent(child);
									importedSceneNode.add(child);
								}
							});
						} else {
							// 原始模型，直接添加到ImportedScene
							if (!importedSceneNode.children.includes(this.state.currentModel)) {
								reparent(this.state.currentModel);
								importedSceneNode.add(this.state.currentModel);
							}
						}
					}
					
					// 添加SMPL网格（如果有，静态显示）
					if (this.state.smplMesh && !importedSceneNode.children.includes(this.state.smplMesh)) {
						reparent(this.state.smplMesh);
						importedSceneNode.add(this.state.smplMesh);
					}
					
					// 添加原始动画剪辑（避免重复）
					if (this.state.currentAnimations && this.state.currentAnimations.length > 0) {
						this.state.currentAnimations.forEach(clip => {
							if (!processedAnimationClips.has(clip.name)) {
								allAnimations.push(clip);
								processedAnimationClips.add(clip.name);
							}
						});
					}
				}
				
				// ============== 自定义相机动画 ==============
				const customCamerasData = {};
				
				this.state.cameras.custom.forEach(camera => {
					// 跳过已经标记为已导出的相机，重新创建数据避免累积
					if (camera.userData.keyframes && camera.userData.keyframes.length > 0) {
						// 确保相机被添加到场景（不在ImportedScene中）
						if (!exportScene.children.includes(camera)) {
							reparent(camera);
							exportScene.add(camera);
						}
						
						// 构建自定义相机数据
						const customCameraData = {
							controlsTarget: camera.userData.controlsTarget ? camera.userData.controlsTarget.toArray() : [0, 0, 0],
							rollAngle: camera.userData.rollAngle || 0,
							upVector: camera.userData.upVector ? camera.userData.upVector.toArray() : [0, 1, 0],
							initialDistance: camera.userData.initialDistance || 5,
							actualZoomFactor: camera.userData.actualZoomFactor || 1.0,
							viewHeight: camera.userData.viewHeight,
							keyframes: camera.userData.keyframes.map(kf => {
								const keyframeData = {
									frame: kf.frame,
									position: this.vectorToArray(kf.position),
									fov: kf.fov,
									controlsTarget: this.vectorToArray(kf.controlsTarget),
									roll: kf.roll || 0,
									isOrthographic: kf.isOrthographic !== undefined ? kf.isOrthographic : camera.isOrthographicCamera
								};
								
								// 处理旋转
								if (kf.quaternion) {
									keyframeData.quaternion = this.quaternionToArray(kf.quaternion);
								} else if (kf.rotation) {
									keyframeData.rotation = this.eulerToArray(kf.rotation);
								}
								
								return keyframeData;
							})
						};
						
						// 使用相机名称作为键
						customCamerasData[camera.name] = customCameraData;
						
						// 标记为已导出的数据
						camera.userData.isExportedData = true;
						
						// 原始的自定义相机没有animation clip
						// 动画保存在userData.keyframes中
						// 如需要支持其他gltf工具查看
						// 可创建动画剪辑（只包含位置旋转，不包含fov/roll）
						/* const clip = this.createAnimationClipFromKeyframes(camera, camera.userData.keyframes, 'custom');
						if (clip) {
							allAnimations.push(clip);
						} */
					}
				});
				
				// 合并自定义相机数据
				if (Object.keys(customCamerasData).length > 0) {
					exportScene.userData.customCameras = customCamerasData;
				}
				
				// ============== 场景相机动画（预处理完） ==============
				const sceneCamerasData = {};
				const targetNodesData = {};
				
				this.state.cameras.scene.forEach(camera => {
					// 只处理有动画关键帧的场景相机
					if (camera.userData.animationKeyframes && camera.userData.animationKeyframes.length > 0) {
						// 确保相机被添加到场景
						if (!exportScene.children.includes(camera)) {
							reparent(camera);
							exportScene.add(camera);
						}
						
						// 从动画关键帧创建动画剪辑
						const clip = this.createAnimationClipFromKeyframes(camera, camera.userData.animationKeyframes, 'scene');
						if (clip && !processedAnimationClips.has(clip.name)) {
							allAnimations.push(clip);
							processedAnimationClips.add(clip.name);
							camera.userData.animationClipName = clip.name;
						}
						
						// 构建场景相机数据
						const sceneCameraData = {
							cameraType: camera.userData.cameraType || 'free',
							keyframes: camera.userData.animationKeyframes.map(kf => {
								const keyframeData = {
									frame: kf.frame,
									position: this.vectorToArray(kf.position),
									rotation: this.eulerToArray(kf.rotation),
									fov: kf.fov,
									roll: kf.roll || 0,
									upVector: this.vectorToArray(kf.upVector)
								};
								
								if (kf.targetPosition) {
									keyframeData.targetPosition = this.vectorToArray(kf.targetPosition);
								}
								
								if (kf.quaternion) {
									keyframeData.quaternion = this.quaternionToArray(kf.quaternion);
								}
								
								return keyframeData;
							}),
							fbxCorrectionApplied: camera.userData.appliedRotationCorrection || false,
							fbxCorrectionQuaternion: camera.userData.fbxCorrectionQuaternion ? 
								this.quaternionToArray(camera.userData.fbxCorrectionQuaternion) : null
						};
						
						sceneCamerasData[camera.name] = sceneCameraData;
						
						// 处理目标节点
						if (camera.userData.cameraType === 'target' && camera.userData.targetNode) {
							const targetNode = camera.userData.targetNode;
							const targetNodeName = targetNode.name;
							
							if (targetNode.userData.animationKeyframes && targetNode.userData.animationKeyframes.length > 0) {
								// 确保目标节点被添加到场景
								if (!exportScene.children.includes(targetNode)) {
									reparent(targetNode);
									exportScene.add(targetNode);
								}
								
								// 为目标节点创建动画剪辑
								const targetClip = this.createAnimationClipFromKeyframes(targetNode, targetNode.userData.animationKeyframes, 'target');
								if (targetClip && !processedAnimationClips.has(targetClip.name)) {
									allAnimations.push(targetClip);
									processedAnimationClips.add(targetClip.name);
								}
								
								// 保存目标节点数据
								targetNodesData[targetNodeName] = {
									keyframes: targetNode.userData.animationKeyframes.map(kf => ({
										frame: kf.frame,
										position: this.vectorToArray(kf.position),
										rotation: this.eulerToArray(kf.rotation)
									})),
									isTargetNode: true,
									associatedCamera: camera.name
								};
								
								// 在相机数据中记录目标节点名称
								sceneCamerasData[camera.name].targetNodeName = targetNodeName;
							}
						}
						
						// 标记为已导出的数据
						camera.userData.isExportedData = true;
					}
				});
				
				// 合并场景相机数据
				if (Object.keys(sceneCamerasData).length > 0) {
					exportScene.userData.sceneCameras = sceneCamerasData;
				}
				
				// 合并目标节点数据
				if (Object.keys(targetNodesData).length > 0) {
					exportScene.userData.targetNodes = targetNodesData;
				}
				
				// 设置导出选项
				const options = { 
					binary: true, 
					trs: false,
					onlyVisible: false,
					truncateDrawRange: false,
					animations: allAnimations,
					includeCustomExtensions: true,
					includeUserData: true
				};
				
				const backupCamerasUserData = new Map();
				
				// 备份并清理相机userData
				this.state.cameras.scene.forEach(cam => {
					backupCamerasUserData.set(cam, cam.userData);
					cam.userData = { _exported: true }; // 只保留标记
				});
				
				// 在restore函数中恢复
				const restore = () => {
					// 恢复相机的userData
					// 避免出现cyclic reference警告 
					backupCamerasUserData.forEach((userData, camera) => {
						camera.userData = userData;
					});
					
					restoreInfo.forEach((info) => {
						if (info.parent !== undefined) {
							const { object, parent, visible } = info;
							if (parent) parent.add(object);
							object.visible = visible;
						}
					});
				};
				
				this.exporter.parse(exportScene, (gltf) => {
					restore();
					
					const fileSize = gltf.byteLength / 1024;
					
					// gltf 是 ArrayBuffer，直接创建 Blob
					const blob = new Blob([gltf], { type: 'model/gltf-binary' }); 
					const link = document.createElement('a'); 
					link.href = URL.createObjectURL(blob); 
					link.download = 'exported_scene.glb'; 
					link.click(); 
					URL.revokeObjectURL(link.href);
					
					this.showMessage("Export completed successfully (" + fileSize.toFixed(2) + " KB)", 5000);
				}, (err) => { 
					restore();
					this.showMessage("Export failed: " + err.message, 5000);
				}, options);
			}

			detectExportedScene(object) {
				// 防御性检查：确保对象存在且是Object3D
				if (!object || !object.isObject3D) {
					return {
						isExported: false,
						isImported: false,
						sceneType: 'unknown',
						originalName: null,
						baseScene: null
					};
				}
				
				const result = {
					isExported: false,
					isImported: false,
					sceneType: 'unknown',
					originalName: object.name || '',
					baseScene: null
				};
				
				const objectName = object.name || '';
				
				// 检查对象名称
				if (objectName === 'ExportedScene' || objectName.startsWith('ExportedScene_')) {
					result.isExported = true;
					result.sceneType = 'exported';
					
					// 尝试查找真正的原始场景
					object.traverse(child => {
						const childName = child.name || '';
						if (childName === 'ImportedScene' || 
							(child.userData && child.userData.name === 'ImportedScene')) {
							result.baseScene = child;
							result.isImported = true;
						}
					});
				} else if (objectName === 'ImportedScene') {
					result.isImported = true;
					result.sceneType = 'imported';
					result.baseScene = object;
				}
				
				// 检查userData中的标记
				if (object.userData) {
					if (object.userData.originalSceneName) {
						result.sceneType = 're-exported';
						result.originalSceneName = object.userData.originalSceneName;
					}
					
					// 如果userData中明确标记了场景类型
					if (object.userData.isExportedScene) {
						result.isExported = true;
						result.sceneType = 'exported';
					}
					if (object.userData.isImportedScene) {
						result.isImported = true;
						result.sceneType = 'imported';
					}
					
					// 检查是否包含相机数据标记
					if (object.userData.sceneCameras || object.userData.customCameras) {
						result.isExported = true;
						result.sceneType = 'exported';
					}
				}
				
				return result;
			}

			exportSMPLAnimation(smplData, exportScene, allAnimations) {
				const numFrames = smplData.numFrames;
				const numVerts = smplData.numVerts;
				const faces = smplData.faces;
				const vertices = smplData.vertices;
				const fps = this.state.playback.fps;
				const totalTime = numFrames / fps;
				
				// 收集所有网格的可见性关键帧数据
				const smplVisibilityData = {
					fps: fps,
					totalFrames: numFrames,
					totalTime: totalTime,
					visibilityKeyframes: []
				};
				
				// 创建所有网格
				const meshes = [];
				for (let frame = 0; frame < numFrames; frame++) {
					// 提取当前帧的顶点数据
					const start = frame * numVerts * 3;
					const end = start + numVerts * 3;
					const frameVerts = vertices.subarray(start, end);
					
					// 创建当前帧的几何体
					const geometry = new THREE.BufferGeometry();
					geometry.setAttribute('position', new THREE.BufferAttribute(frameVerts, 3));
					
					// 复制面索引数据
					const facesArray = new Uint32Array(faces.length);
					facesArray.set(faces);
					geometry.setIndex(new THREE.BufferAttribute(facesArray, 1));
					
					geometry.computeVertexNormals();
					
					// 创建材质
					const material = this.createDefaultMaterial();
					
					// 创建网格并命名
					const meshName = "SMPL_Frame_" + frame.toString().padStart(4, '0');
					const mesh = new THREE.Mesh(geometry, material);
					mesh.name = meshName;
					mesh.userData.isSMPLFrame = true;
					mesh.userData.frameIndex = frame;
					
					// 设置初始可见性：只有第1帧可见
					mesh.visible = (frame === 1);
					
					// 记录可见性关键帧数据
					smplVisibilityData.visibilityKeyframes.push({
						frame: frame,
						meshName: meshName,
						visible: (frame === 1)
					});
					
					// 添加到导出场景和数组
					exportScene.add(mesh);
					meshes.push(mesh);
				}
				
				// 将可见性动画数据存储在场景的userData中
				if (!exportScene.userData.smplAnimation) {
					exportScene.userData.smplAnimation = {};
				}
				
				exportScene.userData.smplAnimation.visibility = smplVisibilityData;
				
				// 不需要创建可见性动画剪辑，因为GLTFExporter不支持
				// 数据已经存储在userData中，导入时会读取
				
				// 为了向后兼容，创建一个空的动画剪辑（不包含轨道）
				// 这样动画混合器可以工作，但实际动画逻辑需要在导入后从userData重建
				const placeholderClip = new THREE.AnimationClip(
					'SMPL_Placeholder_Animation',
					totalTime,
					[]  // 空轨道
				);
				allAnimations.push(placeholderClip);
				
				return {
					meshes: meshes,
					visibilityData: smplVisibilityData
				};
			}

			createAnimationClipFromKeyframes(object, keyframes, type = 'scene') {
				if (!keyframes || keyframes.length === 0) return null;
				
				const objectName = object.name;
				if (!objectName) {
					return null;
				}
				
				// 检查是否已经有相同名称的动画剪辑
				const clipName = "Action_" + objectName;
				
				// 如果对象已经有动画剪辑名称，并且与要创建的相同，则返回null
				if (object.userData && object.userData.animationClipName === clipName) {
					// 这个动画剪辑已经存在
					return null;
				}
				
				// 准备数据数组
				const positionTimes = [];
				const positionValues = [];
				const rotationTimes = [];
				const rotationValues = [];
				const fovTimes = [];
				const fovValues = [];
				const rollTimes = [];
				const rollValues = [];
				
				// 对关键帧按帧号排序
				const sortedKeyframes = [...keyframes].sort((a, b) => a.frame - b.frame);
				
				sortedKeyframes.forEach(kf => {
					const frame = kf.frame;
					const time = frame / this.state.playback.fps;
					
					// 位置轨道
					if (kf.position) {
						positionTimes.push(time);
						if (kf.position.isVector3) {
							positionValues.push(kf.position.x, kf.position.y, kf.position.z);
						} else if (Array.isArray(kf.position)) {
							positionValues.push(kf.position[0], kf.position[1], kf.position[2]);
						} else {
							positionValues.push(kf.position.x || 0, kf.position.y || 0, kf.position.z || 0);
						}
					}
					
					// 旋转轨道（使用四元数）
					rotationTimes.push(time);
					let q = new THREE.Quaternion();
					
					if (kf.quaternion && (kf.quaternion.isQuaternion || kf.quaternion.w !== undefined)) {
						q.copy(kf.quaternion);
					} else if (kf.rotation) {
						 if (kf.rotation.isEuler) {
							q.setFromEuler(kf.rotation);
						} else {
							// 处理 Euler 对象或数组
							const x = kf.rotation.x || (Array.isArray(kf.rotation) ? kf.rotation[0] : 0);
							const y = kf.rotation.y || (Array.isArray(kf.rotation) ? kf.rotation[1] : 0);
							const z = kf.rotation.z || (Array.isArray(kf.rotation) ? kf.rotation[2] : 0);
							q.setFromEuler(new THREE.Euler(x, y, z));
						}
					}
					rotationValues.push(q.x, q.y, q.z, q.w);
				});
				
				// 创建轨道 - 使用绝对路径（模仿原生GLB格式）
				const tracks = [];
				
				if (positionTimes.length > 0) {
					// 使用绝对路径，格式: "Camera001.position"
					const positionTrack = new THREE.VectorKeyframeTrack(
						objectName + '.position',
						positionTimes,
						positionValues
					);
					tracks.push(positionTrack);
				}
				
				if (rotationTimes.length > 0) {
					// 使用绝对路径，格式: "Camera001.quaternion"
					const rotationTrack = new THREE.QuaternionKeyframeTrack(
						objectName + '.quaternion',
						rotationTimes,
						rotationValues
					);
					tracks.push(rotationTrack);
				}
				
				if (tracks.length === 0) {
					return null;
				}
				
				// 创建剪辑
				const duration = Math.max(
					positionTimes[positionTimes.length - 1] || 0, 
					rotationTimes[rotationTimes.length - 1] || 0
				);
				
				const clip = new THREE.AnimationClip(clipName, duration, tracks);
				
				// 标记对象使用的动画剪辑名称
				object.userData.animationClipName = clipName;
				
				return clip;
			}

			// 动画播放录像系统
			updateVisuals(frame) {
				let displayFrame = frame;
				const { currentFormat, smplData, smplMesh, currentMixer, currentAnimations, playback } = this.state;
				
				if (currentFormat === 'bin' && frame < 1 && smplData && smplData.numFrames > 0) {
					displayFrame = 1;
				}
				
				if (currentFormat === 'bin' && smplMesh && smplData) {
					const f = Math.min(Math.max(0, Math.floor(displayFrame)), smplData.numFrames - 1);
					const start = f * smplData.numVerts * 3;
					const end = start + smplData.numVerts * 3;
					smplMesh.geometry.attributes.position.array.set(smplData.vertices.subarray(start, end));
					smplMesh.geometry.attributes.position.needsUpdate = true;
					smplMesh.geometry.computeVertexNormals();
				}
				
				if (currentFormat === 'glb' || currentFormat === 'fbx') {
					if (currentMixer && currentAnimations.length > 0) {
						const clip = currentAnimations[0];
						const duration = clip.duration;
						let time;
						
						if (frame < 0) time = 0;
						else if (frame >= playback.totalFrames) time = duration - 0.0001;
						else {
							time = (frame / playback.totalFrames) * duration;
							if (frame >= playback.totalFrames) time = duration - 0.0001;
						}
						
						time = Math.max(0, time);
						currentMixer.setTime(time);
						currentMixer.update(0);
						
						// 检查是否有SMPL可见性动画
						if (this.state.smplData && this.state.smplData.smplFrames) {
							this.updateSMPLVisibility(frame);
						}
						
						// 确保动画动作存在并激活
						if (currentMixer._actions && currentMixer._actions.length === 0) {
							// 如果没有动作，创建一个
							const action = currentMixer.clipAction(clip);
							action.play();
						} else if (currentMixer._actions.length > 0) {
							// 确保动作是激活的
							const action = currentMixer._actions[0];
							if (!action.isRunning()) {
								action.play();
							}
						}
						
						// 场景相机：应用当前帧的动画数据
						this.updateAllSceneCameraPose(frame);
					} else {
						// 即使没有动画混合器，也要检查SMPL可见性
						if (this.state.smplData && this.state.smplData.smplFrames) {
							this.updateSMPLVisibility(frame);
						}
					}
				}
				
				// 更新所有自定义相机（可视化）姿态
				this.updateAllCustomCameraPose(frame);
				
				// 当前为自定义相机且启用了相机动画，需要更新姿态
				if (this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled) {
					this.updateCurrentCustomCameraPose(frame);
					this.updateUIValuesFromCustomCamera();
				}
				
				// 如果是场景相机，也需要更新UI
				if (this.state.cameras.currentType === 'scene') {
					this.updateUIValuesFromCustomCamera();
				}
				
				// 此处绝对不能更新orbit control，会产生更新bug
				/* this.controls.update(); */
				this.updateVisualizationPoses();
				
				this.updateFPSInfo(frame);
				
				// 渲染路径选择
				this.performRendering();
			}

			updateVisualsToFrame(targetFrame, skipCameraUpdate = false) {
				// 从现有的updateVisuals方法中提取逻辑，但跳过相机更新
				const displayFrame = targetFrame;
				const { currentFormat, smplData, smplMesh, currentMixer, currentAnimations, playback } = this.state;
				
				if (currentFormat === 'bin' && targetFrame < 1 && smplData && smplData.numFrames > 0) {
					targetFrame = 1;
				}
				
				if (currentFormat === 'bin' && smplMesh && smplData) {
					const f = Math.min(Math.max(0, Math.floor(targetFrame)), smplData.numFrames - 1);
					const start = f * smplData.numVerts * 3;
					const end = start + smplData.numVerts * 3;
					smplMesh.geometry.attributes.position.array.set(smplData.vertices.subarray(start, end));
					smplMesh.geometry.attributes.position.needsUpdate = true;
					smplMesh.geometry.computeVertexNormals();
				}
				
				if ((currentFormat === 'glb' || currentFormat === 'fbx') && currentMixer && currentAnimations.length > 0) {
					const clip = currentAnimations[0];
					const duration = clip.duration;
					let time;
					
					if (targetFrame < 0) time = 0;
					else if (targetFrame >= playback.totalFrames) time = duration - 0.0001;
					else {
						time = (targetFrame / playback.totalFrames) * duration;
						if (targetFrame >= playback.totalFrames) time = duration - 0.0001;
					}
					
					time = Math.max(0, time);
					currentMixer.setTime(time);
					currentMixer.update(0);
					
					// 检查是否有SMPL可见性动画
					if (this.state.smplData && this.state.smplData.smplFrames) {
						this.updateSMPLVisibility(targetFrame);
					}
					
					// 确保动画动作存在并激活
					if (currentMixer._actions && currentMixer._actions.length === 0) {
						const action = currentMixer.clipAction(clip);
						action.play();
					} else if (currentMixer._actions.length > 0) {
						const action = currentMixer._actions[0];
						if (!action.isRunning()) {
							action.play();
						}
					}
					
					// 场景相机：如果需要，应用当前帧的动画数据
					if (!skipCameraUpdate) {
						this.updateAllSceneCameraPose(targetFrame);
					}
				}
				
				// 自定义相机：如果需要，更新姿态
				if (!skipCameraUpdate) {
					this.updateAllCustomCameraPose(targetFrame);
					
					// 当前为自定义相机且启用了相机动画，需要更新姿态
					if (this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled) {
						this.updateCurrentCustomCameraPose(targetFrame);
					}
				}
				
				// 检查SMPL可见性（即使没有动画混合器）
				if (this.state.smplData && this.state.smplData.smplFrames) {
					this.updateSMPLVisibility(targetFrame);
				}
			}

			updateFPS() {
				const input = this.dom.inputs.fps;
				let newFPS = parseInt(input.value);
				
				if (newFPS < 1) {
					newFPS = 1;
				} else if (newFPS > 120) {
					newFPS = 120;
				}
				
				// 确保是整数
				newFPS = Math.floor(newFPS);
				input.value = newFPS.toString();
				this.state.playback.fps = newFPS;
			}

			applyFrameRange() {
				const startInput = this.dom.inputs.startFrame;
				const endInput = this.dom.inputs.endFrame;
				
				// 清除状态
				startInput.classList.remove('pending', 'invalid');
				startInput.style.borderColor = '';
				endInput.classList.remove('pending', 'invalid');
				endInput.style.borderColor = '';
				
				// 获取并限制范围
				let newStart = parseInt(startInput.value);
				let newEnd = parseInt(endInput.value);
				
				if (newStart < -9999) newStart = -9999;
				else if (newStart > 9999) newStart = 9999;
				
				if (isNaN(newEnd)) {
					newEnd = this.state.playback.endFrame;
				}
				
				if (newEnd < newStart) newEnd = newStart;
				else if (newEnd > 9999) newEnd = 9999;
				
				// 更新输入框为边界值
				startInput.value = newStart;
				endInput.value = newEnd;
				
				// 应用范围
				if (newStart <= newEnd) {
					this.state.playback.startFrame = newStart;
					this.state.playback.endFrame = newEnd;
					this.dom.inputs.slider.min = newStart;
					this.dom.inputs.slider.max = newEnd;
					
					if (this.state.playback.currentFrame < newStart) {
						this.seek(newStart);
					} else if (this.state.playback.currentFrame > newEnd) {
						this.seek(newEnd);
					}
					
					this.updateTimeSleder();
					this.onWindowResize();
				}
			}

			applySceneLength() {
				const pb = this.state.playback;
				const hasAnimation = pb.totalFrames > 1;
				
				if (hasAnimation) {
					// 有场景动画：按实际动画长度设置
					pb.endFrame = pb.totalFrames - 1;
				} else {
					// 没有场景动画，检查自定义相机的动画
					let customCameraMaxFrames = 0;
					let hasCustomCameraAnimation = false;
					
					// 检查所有自定义相机的关键帧
					this.state.cameras.custom.forEach(camera => {
						if (camera.userData.keyframes && camera.userData.keyframes.length >= 2) {
							hasCustomCameraAnimation = true;
							
							// 找出最小帧和最大帧
							let minFrame = Infinity;
							let maxFrame = -Infinity;
							
							camera.userData.keyframes.forEach(k => {
								if (k.frame < minFrame) minFrame = k.frame;
								if (k.frame > maxFrame) maxFrame = k.frame;
							});
							
							// 只有当最小帧和最大帧不同，表示有动画范围
							if (minFrame < maxFrame) {
								const frameRange = maxFrame - minFrame + 1;
								customCameraMaxFrames = Math.max(customCameraMaxFrames, frameRange);
							}
						}
					});
					
					if (hasCustomCameraAnimation && customCameraMaxFrames > 0) {
						// 有自定义相机动画：使用自定义相机动画的最大帧范围
						pb.endFrame = customCameraMaxFrames - 1;
					} else {
						// 无动画但有模型，或空场景：恢复默认帧范围
						pb.endFrame = this.state.defaultSettings.endFrame; // 149
					}
				}
				
				this.dom.inputs.slider.min = this.state.defaultSettings.startFrame; // 0
				this.dom.inputs.slider.max = pb.endFrame;
				pb.startFrame = this.state.defaultSettings.startFrame; // 0
				
				if (pb.currentFrame > pb.endFrame) {
					this.seek(pb.endFrame);
				}
				
				// 更新输入框显示
				this.dom.inputs.startFrame.value = pb.startFrame.toString();
				this.dom.inputs.endFrame.value = pb.endFrame.toString();
				
				this.updateTimeSleder();
				this.updateInfoDisplay();
			}

			updateTimeSleder() {
				this.dom.inputs.slider.value = Math.floor(this.state.playback.currentFrame);
				this.dom.displays.frame.textContent = Math.floor(this.state.playback.currentFrame) + ' / ' + this.state.playback.endFrame;
			}

			updateKeyframeCount() {
				const count = this.camera.userData.keyframes ? this.camera.userData.keyframes.length : 0;
				this.dom.labels.keyCount.textContent = count + " 🔑";
			}

			togglePlay() {
				const pb = this.state.playback;
				
				if (pb.isPlaying && !pb.isReversed) {
					this.pause();
				} else {
					pb.isReversed = false;
					this.play();
				}
			}

			toggleReversePlay() {
				const pb = this.state.playback;
				
				if (pb.isPlaying && pb.isReversed) {
					this.pause();
				} else {
					pb.isReversed = true;
					this.play();
				}
			}

			play() {
				this.state.playback.isPlaying = true;
				
				if (this.state.currentMixer && this.state.currentMixer._actions && this.state.currentMixer._actions.length > 0) {
					const action = this.state.currentMixer._actions[0];
					if (!action.isRunning()) action.play();
				}
				
				const b = this.dom.btns;
				
				if (this.state.playback.isReversed) {
					b.reverse.textContent = "⏸️";
					b.play.textContent = "▶️";
				} else {
					b.play.textContent = "⏸️";
					b.reverse.textContent = "◀️";
				}
				
				this.state.playback.clock.start();
			}

			pause() {
				this.state.playback.isPlaying = false;
				this.dom.btns.play.textContent = "▶️";
				this.dom.btns.reverse.textContent = "◀️";
			}

			seek(frame) {
				const pb = this.state.playback;
				pb.currentFrame = Math.max(pb.startFrame, Math.min(frame, pb.endFrame));
				this.updateTimeSleder();
				
				this.updateVisuals(Math.floor(pb.currentFrame));
			}

			animate() {
				requestAnimationFrame(() => this.animate());
				const pb = this.state.playback;
				
				if (pb.isPlaying) {
					const delta = pb.clock.getDelta();
					
					if (delta > 0) {
						if (pb.isReversed) {
							pb.currentFrame -= delta * pb.fps;
							if (pb.currentFrame < pb.startFrame) pb.currentFrame = pb.endFrame;
						} else {
							pb.currentFrame += delta * pb.fps;
							if (pb.currentFrame > pb.endFrame) {
								pb.currentFrame = pb.startFrame;
								if (this.state.recording.isRecording) {
									this.pause();
									if (this.state.recording.mediaRecorder?.state === 'recording') {
										this.state.recording.mediaRecorder.stop();
									}
								}
							}
						}
					}
				}
				
				this.seek(pb.currentFrame);
			}

			goToFirstFrame() { 
				const pb = this.state.playback;
				if (pb.isPlaying) this.pause();
				this.seek(pb.startFrame);
			}

			goToLastFrame() {
				const pb = this.state.playback;
				if (pb.isPlaying) this.pause();
				this.seek(pb.endFrame);
			}

			goToPrevKeyframe() {
				const f = Math.floor(this.state.playback.currentFrame);
				const keyframes = this.state.cameraAnim.keyframes;
				
				if (keyframes.length === 0) return;
				
				if (this.state.playback.isPlaying) this.pause();
				
				const sortedKeyframes = [...keyframes].sort((a, b) => a.frame - b.frame);
				const prevKeyframes = sortedKeyframes.filter(k => k.frame < f);
				
				if (prevKeyframes.length > 0) {
					const prevKey = prevKeyframes[prevKeyframes.length - 1];
					this.seek(prevKey.frame);
				} else {
					const lastKey = sortedKeyframes[sortedKeyframes.length - 1];
					this.seek(lastKey.frame);
				}
			}

			goToNextKeyframe() {
				const f = Math.floor(this.state.playback.currentFrame);
				const keyframes = this.state.cameraAnim.keyframes;
				
				if (keyframes.length === 0) return;
				
				if (this.state.playback.isPlaying) this.pause();
				
				const sortedKeyframes = [...keyframes].sort((a, b) => a.frame - b.frame);
				const nextKeyframes = sortedKeyframes.filter(k => k.frame > f);
				
				if (nextKeyframes.length > 0) {
					const nextKey = nextKeyframes[0];
					this.seek(nextKey.frame);
				} else {
					const firstKey = sortedKeyframes[0];
					this.seek(firstKey.frame);
				}
			}

			goToPrevFrame() {
				const pb = this.state.playback;
				if (pb.isPlaying) this.pause();
				
				let newFrame = Math.floor(pb.currentFrame) - 1;
				
				if (newFrame < pb.startFrame) {
					newFrame = pb.endFrame;
				}
				
				this.seek(newFrame);
			}

			goToNextFrame() {
				const pb = this.state.playback;
				if (pb.isPlaying) this.pause();
				
				let newFrame = Math.floor(pb.currentFrame) + 1;
				
				if (newFrame > pb.endFrame) {
					newFrame = pb.startFrame;
				}
				
				this.seek(newFrame);
			}

			onTimeSliderInput(e) {
				const targetFrame = parseInt(e.target.value);
				if (this.state.playback.isPlaying) this.pause();
				this.seek(targetFrame);
			}

			// 录像系统
			startRecording() {
				if (this.state.recording.isRecording) return;
				
				this.state.recording.originalGridVisible = this.dom.toggles.helper.checked;
				this.state.recording.originalInfoVisible = this.dom.toggles.info.checked;
				
				this.dom.toggles.helper.checked = false;
				this.dom.toggles.info.checked = false;
				
				this.toggleHelper();
				this.toggleInfoDisplay();
				
				this.state.recording.isRecording = true;
				this.dom.btns.record.classList.add('recording');
				this.state.recording.chunks = [];
				
				try {
					const stream = this.renderer.domElement.captureStream(this.state.playback.fps);
					const mimeTypes = ['video/webm; codecs=vp9', 'video/webm; codecs=vp8', 'video/webm'];
					let mimeType = '';
					for (let i=0; i<mimeTypes.length; i++) {
						if (MediaRecorder.isTypeSupported(mimeTypes[i])) {
							mimeType = mimeTypes[i]; break;
						}
					}
					
					if (!mimeType) mimeType = 'video/webm';
					
					this.state.recording.mediaRecorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 5000000 });
					
					this.state.recording.mediaRecorder.ondataavailable = (e) => {
						if (e.data.size > 0) this.state.recording.chunks.push(e.data);
					};
					
					this.state.recording.mediaRecorder.onstop = () => {
						if (this.state.recording.chunks.length === 0) {
							this.showMessage("Recording failed: No data recorded", 5000);
						} else {
							try {
								const blob = new Blob(this.state.recording.chunks, { type: 'video/webm' });
								const url = URL.createObjectURL(blob);
								const a = document.createElement('a');
								a.href = url;
								a.download = 'recording_' + Date.now() + '.webm';
								document.body.appendChild(a);
								a.click();
								document.body.removeChild(a);
								URL.revokeObjectURL(url);
							} catch (e) {
								alert("Error saving recording: " + e.message);
							}
						}
						
						this.dom.toggles.helper.checked = this.state.recording.originalGridVisible;
						this.dom.toggles.info.checked = this.state.recording.originalInfoVisible;
						
						this.toggleHelper();
						this.toggleInfoDisplay();
						
						this.state.recording.isRecording = false;
						this.dom.btns.record.classList.remove('recording');
					};
					
					this.state.recording.mediaRecorder.onerror = () => { 
						this.showMessage("Recording error occurred", 5000); 
					};
					
					this.state.recording.mediaRecorder.start(100);
					this.seek(this.state.playback.startFrame);
					this.state.playback.isReversed = false;
					this.play();
					
					const checkEnd = () => {
						if (this.state.recording.isRecording && this.state.playback.currentFrame >= this.state.playback.endFrame) {
							this.pause();
							if (this.state.recording.mediaRecorder && this.state.recording.mediaRecorder.state === 'recording') {
								this.state.recording.mediaRecorder.stop();
							}
						} else if (this.state.recording.isRecording) {
							setTimeout(checkEnd, 1000 / this.state.playback.fps);
						}
					};
					
					checkEnd();
				} catch (e) { 
					this.showMessage("Recording setup failed: " + e.message, 5000); 
				}
			}

			// 材质系统
			initializeMaterialAndLightModes() {
				this.state.materialMode = 'original';
				
				// 设置下拉菜单默认值
				const materialSelect = document.getElementById('material-mode-select');
				if (materialSelect) {
					materialSelect.value = 'original';
				}
				
				this.state.materialParams.default.color = this.state.defaultSettings.meshColor;
				this.state.commonParams.background = this.state.defaultSettings.bgColor;
				
				// 应用初始材质
				this.applyMaterialMode();
				
				// 初始状态下禁用颜色选择器
				this.updateBgColorPickerState('original');
				
				// 灯光模式初始化（保持不变）
				this.state.useSceneLight = false;
				
				// 同步UI状态 - 灯光
				if (this.dom.toggles.light) {
					this.dom.toggles.light.checked = false;
					this.dom.toggles.light.classList.remove('disabled-control');
					this.dom.toggles.light.classList.add('enabled-control');
				}
				
				if (this.dom.labels.lightLabel) {
					this.dom.labels.lightLabel.textContent = "Default Light";
					this.dom.labels.lightLabel.classList.remove('disabled-control');
					this.dom.labels.lightLabel.classList.add('enabled-control');
				}
				
				// 阴影开关初始化
				if (this.dom.toggles.shadows) {
					this.dom.toggles.shadows.checked = this.state.lights.shadowsEnabled;
					this.updateShadowsButtonState();
				}
				
				// 应用默认设置
				this.enableDefaultLights();
				
				// 更新灯光强度
				this.updateDirLightIntensity();
				this.updateAmbLightIntensity();
			}

			createDefaultMaterial() {
				if (!this.state.materials.default) {
					const params = this.state.materialParams.default;
					this.state.materials.default = new THREE.MeshStandardMaterial({
						color: new THREE.Color(params.color),
						roughness: params.roughness,
						metalness: params.metalness,
						flatShading: params.flatShading,
						side: this.getSideValue(this.state.commonParams.side),
					});
				}
				return this.state.materials.default;
			}

			createWireframeMaterial() {
				if (!this.state.materials.wireframe) {
					const params = this.state.materialParams.wireframe;
					this.state.materials.wireframe = new THREE.MeshBasicMaterial({
						wireframe: true,
						color: new THREE.Color(params.color),
						linewidth: params.linewidth,
						opacity: params.opacity,
						transparent: false,
						side: this.getSideValue(this.state.commonParams.side)
					});
				}
				return this.state.materials.wireframe;
			}

			createNormalMaterial() {
				if (!this.state.materials.normal) {
					this.state.materials.normal = new THREE.MeshNormalMaterial({
						side: this.getSideValue(this.state.commonParams.side)
					});
				}
				return this.state.materials.normal;
			}

			createDepthMaterial() {
				if (!this.state.materials.depth) {
					this.state.materials.depth = new THREE.MeshDepthMaterial({
						side: this.getSideValue(this.state.commonParams.side)
					});
				}
				return this.state.materials.depth;
			}

			createLineArtMaterial() {
				if (!this.state.materials.lineart) {
					const vertexShader = '\
						varying vec3 vNormal;\
						varying vec3 vViewPosition;\
						void main() {\
							vNormal = normalize(normalMatrix * normal);\
							vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);\
							vViewPosition = -mvPosition.xyz;\
							gl_Position = projectionMatrix * mvPosition;\
						}';
					
					const fragmentShader = '\
						varying vec3 vNormal;\
						varying vec3 vViewPosition;\
						uniform vec3 color;\
						uniform float edgeStart;\
						uniform float edgeEnd;\
						uniform float curvatureStart;\
						uniform float curvatureEnd;\
						void main() {\
							vec3 viewDir = normalize(vViewPosition);\
							float NdotV = 1.0 - dot(vNormal, viewDir);\
							float curvature = length(fwidth(vNormal)) / length(fwidth(vViewPosition));\
							float edge = smoothstep(edgeStart, edgeEnd, NdotV) * smoothstep(curvatureStart, curvatureEnd, curvature);\
							float line = step(0.5, edge);\
							vec3 finalColor = mix(vec3(0.0), color, line);\
							gl_FragColor = vec4(finalColor, 1.0);\
						}';
					
					const params = this.state.materialParams.lineart;
					this.state.materials.lineart = new THREE.ShaderMaterial({
						uniforms: {
							color: { value: new THREE.Color(params.color) },
							edgeStart: { value: params.edgeStart },
							edgeEnd: { value: params.edgeEnd },
							curvatureStart: { value: params.curvatureStart },
							curvatureEnd: { value: params.curvatureEnd }
						},
						vertexShader: vertexShader,
						fragmentShader: fragmentShader,
						side: this.getSideValue(this.state.commonParams.side),
						alphaToCoverage: true
					});
				}
				return this.state.materials.lineart;
			}

			createEdgeMaterial() {
				if (!this.state.materials.edge) {
					const vertexShader = '\
						varying vec3 vPosition;\
						varying vec3 vNormal;\
						varying float vDepth;\
						void main() {\
							vPosition = position;\
							vNormal = normalize(normalMatrix * normal);\
							vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);\
							vDepth = -mvPosition.z;\
							gl_Position = projectionMatrix * mvPosition;\
						}';
					
					const fragmentShader = '\
						varying vec3 vPosition;\
						varying vec3 vNormal;\
						varying float vDepth;\
						uniform vec3 color;\
						uniform float normalThreshold;\
						uniform float posThreshold;\
						uniform float edgeStart;\
						uniform float edgeEnd;\
						uniform float contrast;\
						float sdfEdge(vec3 pos, vec3 normal) {\
							vec3 fNormal = fwidth(normal);\
							vec3 fPos = fwidth(pos);\
							float edgeNormal = length(fNormal);\
							float edgePos = length(fPos);\
							float edge = max(edgeNormal * normalThreshold, edgePos * posThreshold);\
							return smoothstep(edgeStart, edgeEnd, edge);\
						}\
						vec3 sdfGradient(float value) {\
							float intensity = smoothstep(0.0, 1.0, value);\
							return vec3(intensity);\
						}\
						void main() {\
							float edge = sdfEdge(vPosition, vNormal);\
							float depth = vDepth * 0.01;\
							float depthEdge = smoothstep(0.1, 0.3, fract(depth * 5.0));\
							float finalEdge = max(edge, depthEdge * 0.3);\
							vec3 sdfColor = sdfGradient(finalEdge);\
							sdfColor = (sdfColor - 0.5) * contrast + 0.5;\
							vec3 finalColor = mix(vec3(0.0), color, sdfColor);\
							gl_FragColor = vec4(finalColor, 1.0);\
						}';
					
					const params = this.state.materialParams.edge;
					this.state.materials.edge = new THREE.ShaderMaterial({
						uniforms: {
							color: { value: new THREE.Color(params.color) },
							normalThreshold: { value: params.normalThreshold },
							posThreshold: { value: params.posThreshold },
							edgeStart: { value: params.edgeStart },
							edgeEnd: { value: params.edgeEnd },
							contrast: { value: params.contrast }
						},
						vertexShader: vertexShader,
						fragmentShader: fragmentShader,
						side: this.getSideValue(this.state.commonParams.side),
						transparent: false
					});
				}
				return this.state.materials.edge;
			}

			createCannyMaterial() {
				// float cannyLine
				// 边缘阀值（更细）：edgeDetail(0.9)
				// 边缘阀值（更多）：edgeDetail(0.7)
				if (!this.state.materials.canny) {
					const vertexShader = '\
						varying vec3 vPosition;\
						varying vec3 vNormal;\
						varying vec2 vUv;\
						void main() {\
							vPosition = position;\
							vNormal = normalize(normalMatrix * normal);\
							vUv = uv;\
							gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);\
						}';
					
					const fragmentShader = '\
						varying vec3 vPosition;\
						varying vec3 vNormal;\
						varying vec2 vUv;\
						uniform vec3 color;\
						uniform float lowThreshold;\
						uniform float highThreshold;\
						uniform float edgeStrength;\
						uniform float edgeDetail;\
						float cannyEdgeDetection(vec3 pos, vec3 normal, vec2 uv) {\
							vec3 gradient = fwidth(normal);\
							float gradientMagnitude = length(gradient);\
							vec3 posGradient = fwidth(pos);\
							float posGradientMagnitude = length(posGradient);\
							float strength = gradientMagnitude * 2.0 + posGradientMagnitude * 0.5;\
							strength *= edgeStrength;\
							if (strength < lowThreshold) {\
								return 0.0;\
							} else if (strength > highThreshold) {\
								return 1.0;\
							} else {\
								return 0.5;\
							}\
						}\
						float gaussianBlur(float value) {\
							return smoothstep(0.1, 0.9, value);\
						}\
						void main() {\
							float edge = cannyEdgeDetection(vPosition, vNormal, vUv);\
							edge = gaussianBlur(edge);\
							float cannyLine = smoothstep(0.9 - edgeDetail, 1.1 - edgeDetail, edge);\
							vec3 finalColor = mix(vec3(0.0), color, cannyLine);\
							gl_FragColor = vec4(finalColor, 1.0);\
						}';
					
					const params = this.state.materialParams.canny;
					this.state.materials.canny = new THREE.ShaderMaterial({
						uniforms: {
							color: { value: new THREE.Color(params.color) },
							lowThreshold: { value: params.lowThreshold },
							highThreshold: { value: params.highThreshold },
							edgeStrength: { value: params.edgeStrength },
							edgeDetail: { value: params.edgeDetail }
						},
						vertexShader: vertexShader,
						fragmentShader: fragmentShader,
						side: this.getSideValue(this.state.commonParams.side),
						transparent: false
					});
				}
				return this.state.materials.canny;
			}

			initPostProcessing() {
				if (!this.renderer || !this.scene || !this.camera) return;
				
				// === 1. 创建/获取效果合成器 ===
				if (!this.composer) {
					this.composer = new EffectComposer(this.renderer);
				}
				
				// === 2. 清除合成器中所有现有通道 ===
				while (this.composer.passes.length > 0) {
					const pass = this.composer.passes[0];
					if (pass.dispose) pass.dispose();
					this.composer.removePass(pass);
				}
				
				// === 3. 创建并添加渲染通道 ===
				const renderPass = new RenderPass(this.scene, this.camera);
				renderPass.clear = true;
				renderPass.clearColor = new THREE.Color(0x000000);
				renderPass.clearAlpha = 1.0;
				this.composer.addPass(renderPass);
				
				// === 4. 创建法线渲染目标===
				if (!this.normalRenderTarget) {
					const size = this.renderer.getSize(new THREE.Vector2());
					this.normalRenderTarget = new THREE.WebGLRenderTarget(
						size.x, size.y,
						{
							minFilter: THREE.LinearFilter,
							magFilter: THREE.NearestFilter,
							format: THREE.RGBAFormat,
							encoding: THREE.LinearEncoding,
							stencilBuffer: false
						}
					);
				}
				
				// === 5. 创建轮廓检测通道 ===
				if (!this.contourPass) {
					this.createContourPass();
				} else {
					this.contourPass.enabled = this.isContourMode;
				}
				
				// === 6. 创建SSAO通道 ===
				this.createSSAOPass();
				
				// === 7. 创建GTAO通道 ===
				this.createGTAOPass();
				
				// === 8. 设置深度纹理（如果启用）===
				if (!this.depthTexture) {
					this.depthTexture = new THREE.DepthTexture();
					this.depthTexture.type = THREE.UnsignedShortType;
					this.renderer.depthTexture = this.depthTexture;
				}
				
				// === 9. 设置合成器尺寸 ===
				const size = this.renderer.getSize(new THREE.Vector2());
				this.composer.setSize(size.x, size.y);
			}

			updatePostProcessing() {
				// 更新SSAO通道
				if (this.ssaoPass) {
					this.ssaoPass.camera = this.camera;
					if (this.ssaoPass.setCamera) {
						this.ssaoPass.setCamera(this.camera);
					}
					if (this.updateSSAOParameters) {
						this.updateSSAOParameters();
					}
				}
				
				// 更新GTAO通道
				if (this.gtaoPass) {
					this.gtaoPass.camera = this.camera;
					if (this.gtaoPass.setCamera) {
						this.gtaoPass.setCamera(this.camera);
					}
					if (this.UpdateGTAOParameters) {
						this.UpdateGTAOParameters();
					}
				}
				
				// 更新轮廓通道
				if (this.contourPass && this.contourPass.uniforms && this.renderNormalTexture) {
					this.renderNormalTexture();
				}
				
				// 更新RenderPass的相机 - 直接使用保存的引用
				if (this.renderPass) {
					this.renderPass.camera = this.camera;
				}
				
				// 更新后处理合成器
				if (this.composer) {
					this.composer.setSize(
						this.renderer.domElement.width,
						this.renderer.domElement.height
					);
				}
			}

			renderNormalTexture() {
				// 确保渲染目标存在且尺寸正确
				if (!this.normalRenderTarget) {
					const canvas = this.renderer.domElement;
					this.normalRenderTarget = new THREE.WebGLRenderTarget(
						canvas.width,
						canvas.height,
						{
							minFilter: THREE.LinearFilter,
							magFilter: THREE.NearestFilter,
							format: THREE.RGBAFormat,
							encoding: THREE.LinearEncoding
						}
					);
				}
				
				// 渲染法线场景到纹理
				this.renderer.setRenderTarget(this.normalRenderTarget);
				this.renderer.render(this.scene, this.camera);
				this.renderer.setRenderTarget(null);
			}

			createContourPass() {
				// 如果已存在，先清理旧的
				if (this.contourPass) {
					if (this.contourPass.dispose) this.contourPass.dispose();
					this.contourPass = null;
				}
				
				const contourShader = {
					uniforms: {
						tDiffuse: { value: null },
						tNormal: { value: null },
						tDepth: { value: null },
						resolution: { value: new THREE.Vector2() },
						thickness: { value: 1.5 },
						depthThreshold: { value: 0.015 },
						normalThreshold: { value: 0.4 },
						color: { value: new THREE.Color(0xffffff) }
					},
					
					vertexShader: '\
						varying vec2 vUv;\
						void main() {\
							vUv = uv;\
							gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);\
						}',
					
					fragmentShader: '\
						uniform sampler2D tDiffuse;\
						uniform sampler2D tNormal;\
						uniform sampler2D tDepth;\
						uniform vec2 resolution;\
						uniform vec3 color;\
						uniform float thickness;\
						uniform float depthThreshold;\
						uniform float normalThreshold;\
						varying vec2 vUv;\
						float getDepth(vec2 uv) {\
							return texture2D(tDepth, uv).r;\
						}\
						vec3 getNormal(vec2 uv) {\
							return texture2D(tNormal, uv).xyz * 2.0 - 1.0;\
						}\
						float sobelDepth(sampler2D depthTex, vec2 uv) {\
							vec2 texel = thickness / resolution;\
							float topLeft = getDepth(uv + vec2(-1, 1) * texel);\
							float top = getDepth(uv + vec2(0, 1) * texel);\
							float topRight = getDepth(uv + vec2(1, 1) * texel);\
							float left = getDepth(uv + vec2(-1, 0) * texel);\
							float right = getDepth(uv + vec2(1, 0) * texel);\
							float bottomLeft = getDepth(uv + vec2(-1, -1) * texel);\
							float bottom = getDepth(uv + vec2(0, -1) * texel);\
							float bottomRight = getDepth(uv + vec2(1, -1) * texel);\
							\
							float gx = -topLeft - 2.0 * left - bottomLeft + topRight + 2.0 * right + bottomRight;\
							float gy = -topLeft - 2.0 * top - topRight + bottomLeft + 2.0 * bottom + bottomRight;\
							\
							return sqrt(gx * gx + gy * gy);\
						}\
						float checkNormalEdge(vec2 uv) {\
							vec2 texel = thickness / resolution;\
							vec3 centerNormal = getNormal(uv);\
							float maxDiff = 0.0;\
							\
							for (int i = -1; i <= 1; i++) {\
								for (int j = -1; j <= 1; j++) {\
									if (i == 0 && j == 0) continue;\
									vec2 offset = vec2(float(i), float(j)) * texel;\
									vec3 neighborNormal = getNormal(uv + offset);\
									float diff = 1.0 - dot(centerNormal, neighborNormal);\
									maxDiff = max(maxDiff, diff);\
								}\
							}\
							return maxDiff;\
						}\
						void main() {\
							float depthEdge = sobelDepth(tDepth, vUv);\
							float normalEdge = checkNormalEdge(vUv);\
							\
							bool isEdge = depthEdge > depthThreshold || normalEdge > normalThreshold;\
							\
							if (isEdge) {\
								gl_FragColor = vec4(color, 1.0);\
							} else {\
								gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);\
							}\
						}'
				};
				
				this.contourPass = new ShaderPass(contourShader);
				this.contourPass.enabled = this.isContourMode;
				this.contourPass.renderToScreen = true;
				
				if (this.composer) {
					this.composer.addPass(this.contourPass);
				}
				
				// 设置深度纹理
				this.contourPass.uniforms.tDepth.value = this.depthTexture;
			}

			createSSAOPass() {
				// 如果已存在，先清理旧的
				if (this.ssaoPass) {
					if (this.ssaoPass.dispose) this.ssaoPass.dispose();
					this.ssaoPass = null;
				}
				
				const ssaoParams = this.state.postProcessingParams.ssao;
				
				// 创建SSAOPass
				this.ssaoPass = new SSAOPass(
					this.scene,
					this.camera,
					this.renderer.domElement.width,
					this.renderer.domElement.height
				);
				
				// 配置SSAO参数
				this.ssaoPass.kernelRadius = ssaoParams.kernelRadius;	// 采样核半径 (0-32)
				this.ssaoPass.minDistance = ssaoParams.minDistance;		// 最小距离 (0.001-0.02)
				this.ssaoPass.maxDistance = ssaoParams.maxDistance;		// 最大距离 (0.01-0.3)
				this.ssaoPass.output = ssaoParams.output;				// 启用模糊输出
				
				// 默认禁用
				this.ssaoPass.enabled = false;
				this.ssaoPass.renderToScreen = false;
				
				// 添加到合成器
				if (this.composer) {
					this.composer.addPass(this.ssaoPass);
				}
			}

			createGTAOPass() {
				// 如果已存在，先清理旧的
				if (this.gtaoPass) {
					if (this.gtaoPass.dispose) this.gtaoPass.dispose();
					this.gtaoPass = null;
				}
				
				const gtaoParams = this.state.postProcessingParams.gtao;
				
				// 创建GTAOPass
				this.gtaoPass = new GTAOPass(
					this.scene,
					this.camera,
					this.renderer.domElement.width,
					this.renderer.domElement.height
				);
				
				// 配置GTAO参数
				this.gtaoPass.radius = gtaoParams.radius;						// 采样半径 (0.01-1)
				this.gtaoPass.distanceExponent = gtaoParams.distanceExponent;	// 距离指数 (1-4)
				this.gtaoPass.thickness = gtaoParams.thickness;					// 厚度 (0.01-10)
				this.gtaoPass.scale = gtaoParams.scale;							// 比例 (0.01-2.0)
				this.gtaoPass.distanceFallOff = gtaoParams.distanceFallOff;		// 距离衰减 (0-1)
				this.gtaoPass.samples = gtaoParams.samples;						// 采样数 (2-32)
				this.gtaoPass.output = gtaoParams.output;						// 启用去噪输出
				
				// 默认禁用
				this.gtaoPass.enabled = false;
				this.gtaoPass.renderToScreen = false;
				
				// 添加到合成器
				if (this.composer) {
					this.composer.addPass(this.gtaoPass);
				}
			}

			performRendering() {
				// 根据材质模式选择渲染路径
				switch (this.state.materialMode) {
					case 'contour':
						this.renderContourMode();
						break;
					case 'ssao':
						this.renderSSAOMode();
						break;
					case 'gtao':
						this.renderGTAOMode();
						break;
					default:
						this.renderCommonMode();
						break;
				}
			}

			renderCommonMode() {
				// 普通渲染模式，禁用所有后处理通道
				if (this.contourPass) this.contourPass.enabled = false;
				if (this.ssaoPass) this.ssaoPass.enabled = false;
				if (this.gtaoPass) this.gtaoPass.enabled = false;
				
				this.renderer.render(this.scene, this.camera);
			}

			renderContourMode() {
				// 轮廓模式
				if (!this.composer || !this.normalRenderTarget) {
					this.renderCommonMode();
					return;
				}
				
				// 禁用其他AO通道
				if (this.ssaoPass) this.ssaoPass.enabled = false;
				if (this.gtaoPass) this.gtaoPass.enabled = false;
				
				// 动态生成法线纹理
				this.renderNormalTexture();
				
				// 更新轮廓着色器参数
				if (this.contourPass) {
					this.contourPass.uniforms.tNormal.value = this.normalRenderTarget.texture;
					
					if (this.depthTexture) {
						this.contourPass.uniforms.tDepth.value = this.depthTexture;
					}
					
					const size = this.renderer.getSize(new THREE.Vector2());
					this.contourPass.uniforms.resolution.value.copy(size);
					
					this.contourPass.enabled = true;
					this.contourPass.renderToScreen = true;
					
					this.composer.render();
				} else {
					this.renderCommonMode();
				}
			}

			renderSSAOMode() {
				// SSAO模式
				if (!this.composer || !this.ssaoPass) {
					this.renderCommonMode();
					return;
				}
				
				// 禁用其他通道
				if (this.contourPass) this.contourPass.enabled = false;
				if (this.gtaoPass) this.gtaoPass.enabled = false;
				
				// 启用SSAO通道
				this.ssaoPass.enabled = true;
				this.ssaoPass.renderToScreen = true;
				
				// 确保SSAO通道在合成器中的位置正确
				// 查找SSAO通道在合成器中的索引
				let ssaoIndex = -1;
				for (let i = 0; i < this.composer.passes.length; i++) {
					if (this.composer.passes[i] === this.ssaoPass) {
						ssaoIndex = i;
						break;
					}
				}
				
				// 确保SSAO通道是最后一个通道（这样才能渲染到屏幕）
				if (ssaoIndex >= 0 && ssaoIndex < this.composer.passes.length - 1) {
					// 将SSAO通道移到最后一个位置
					const ssaoPass = this.composer.passes.splice(ssaoIndex, 1)[0];
					this.composer.passes.push(ssaoPass);
				}
				
				// 更新SSAO通道尺寸（如果窗口大小改变）
				const size = this.renderer.getSize(new THREE.Vector2());
				if (this.ssaoPass.setSize) {
					this.ssaoPass.setSize(size.x, size.y);
				}
				
				// 使用合成器渲染
				this.composer.render();
			}

			renderGTAOMode() {
				// GTAO模式
				if (!this.composer || !this.gtaoPass) {
					this.renderCommonMode();
					return;
				}
				
				// 禁用其他通道
				if (this.contourPass) this.contourPass.enabled = false;
				if (this.ssaoPass) this.ssaoPass.enabled = false;
				
				// 启用GTAO通道
				this.gtaoPass.enabled = true;
				this.gtaoPass.renderToScreen = true;
				
				// 确保GTAO通道在合成器中的位置正确
				// 查找GTAO通道在合成器中的索引
				let gtaoIndex = -1;
				for (let i = 0; i < this.composer.passes.length; i++) {
					if (this.composer.passes[i] === this.gtaoPass) {
						gtaoIndex = i;
						break;
					}
				}
				
				// 确保GTAO通道是最后一个通道（这样才能渲染到屏幕）
				if (gtaoIndex >= 0 && gtaoIndex < this.composer.passes.length - 1) {
					// 将GTAO通道移到最后一个位置
					const gtaoPass = this.composer.passes.splice(gtaoIndex, 1)[0];
					this.composer.passes.push(gtaoPass);
				}
				
				// 更新GTAO通道尺寸（如果窗口大小改变）
				const size = this.renderer.getSize(new THREE.Vector2());
				if (this.gtaoPass.setSize) {
					this.gtaoPass.setSize(size.x, size.y);
				}
				
				// 使用合成器渲染
				this.composer.render();
			}

			updateDefaultMaterial() {
				const material = this.state.materials.default;
				const params = this.state.materialParams.default;
				
				if (material) {
					material.color.set(params.color);
					material.roughness = params.roughness;
					material.metalness = params.metalness;
					material.side = this.getSideValue(this.state.commonParams.side);
					material.flatShading = params.flatShading;
					material.needsUpdate = true;
				}
			}

			updateWireframeMaterial() {
				const material = this.state.materials.wireframe;
				const params = this.state.materialParams.wireframe;
				
				if (material) {
					material.color.set(params.color);
					material.linewidth = params.linewidth;
					material.opacity = params.opacity;
					material.transparent = params.opacity < 1.0;
					material.side = this.getSideValue(this.state.commonParams.side);
					material.needsUpdate = true;
				}
			}

			updateNormalMaterial() {
				const material = this.state.materials.normal;
				const params = this.state.materialParams.wireframe;
				
				if (material) {
					material.flatShading = params.flatShading;
					material.needsUpdate = true;
				}
			}

			updateLineartMaterial() {
				const material = this.state.materials.lineart;
				const params = this.state.materialParams.lineart;
				
				if (material && material.uniforms) {
					material.uniforms.color.value.set(params.color);
					material.uniforms.edgeStart.value = params.edgeStart;
					material.uniforms.edgeEnd.value = params.edgeEnd;
					material.uniforms.curvatureStart.value = params.curvatureStart;
					material.uniforms.curvatureEnd.value = params.curvatureEnd;
					material.needsUpdate = true;
				}
			}

			updateCannyMaterial() {
				const material = this.state.materials.canny;
				const params = this.state.materialParams.canny;
				
				if (material && material.uniforms) {
					material.uniforms.color.value.set(params.color);
					material.uniforms.lowThreshold.value = params.lowThreshold;
					material.uniforms.highThreshold.value = params.highThreshold;
					material.uniforms.edgeStrength.value = params.edgeStrength;
					material.uniforms.edgeDetail.value = params.edgeDetail;
					material.needsUpdate = true;
				}
			}

			updateEdgeMaterial() {
				const material = this.state.materials.edge;
				const params = this.state.materialParams.edge;
				
				if (material && material.uniforms) {
					material.uniforms.color.value.set(params.color);
					material.uniforms.normalThreshold.value = params.normalThreshold;
					material.uniforms.posThreshold.value = params.posThreshold;
					material.uniforms.edgeStart.value = params.edgeStart;
					material.uniforms.edgeEnd.value = params.edgeEnd;
					material.uniforms.contrast.value = params.contrast;
					material.needsUpdate = true;
				}
			}

			updateContourMaterial() {
				const pass = this.contourPass;
				const params = this.state.materialParams.contour;
				
				if (pass && pass.uniforms) {
					pass.uniforms.color.value.set(params.color);
					pass.uniforms.thickness.value = params.thickness;
					pass.uniforms.depthThreshold.value = params.depthThreshold;
					pass.uniforms.normalThreshold.value = params.normalThreshold;
				}
			}

			updateSSAOParameters() {
				if (!this.ssaoPass) return;
				
				const ssaoParams = this.state.postProcessingParams.ssao;
				
				this.ssaoPass.kernelRadius = ssaoParams.kernelRadius;
				this.ssaoPass.minDistance = ssaoParams.minDistance;
				this.ssaoPass.maxDistance = ssaoParams.maxDistance;
			}

			UpdateGTAOParameters() {
				if (!this.gtaoPass) return;
				
				const gtaoParams = this.state.postProcessingParams.gtao;
				
				this.gtaoPass.radius = gtaoParams.radius;
				this.gtaoPass.distanceExponent = gtaoParams.distanceExponent;
				this.gtaoPass.thickness = gtaoParams.thickness;
				this.gtaoPass.scale = gtaoParams.scale;
				this.gtaoPass.distanceFallOff = gtaoParams.distanceFallOff;
				this.gtaoPass.samples = gtaoParams.samples;
			}

			resetDefaultParameters() {
				const defaultMaterialParams = {
					color: '#4a9eff',
					roughness: 1.0,
					metalness: 0.0,
					flatShading: false
				};
				
				Object.assign(this.state.materialParams.default, defaultMaterialParams);
				this.updateDefaultMaterial();
				
				if (this.state.materialMode === 'default' && this.state.materialGUI.defaultFolder) {
					try {
						this.state.materialGUI.defaultFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.defaultFolder = null;
					this.createDefaultMaterialFolder();
				}
			}

			resetWireframeParameters() {
				const wireframeMaterialParams = {
					color: '#888888',
					linewidth: 1,
					opacity: 1.0,
					transparent: false
				};
				
				Object.assign(this.state.materialParams.wireframe, wireframeMaterialParams);
				this.updateWireframeMaterial();
				
				if (this.state.materialMode === 'wireframe' && this.state.materialGUI.wireframeFolder) {
					try {
						this.state.materialGUI.wireframeFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.wireframeFolder = null;
					this.createWireframeMaterialFolder();
				}
			}

			resetNormalParameters() {
				const defaultNormalParams = {
					flatShading: false
				};
				
				Object.assign(this.state.materialParams.normal, defaultNormalParams);
				this.updateNormalMaterial();
				
				if (this.state.materialMode === 'normal' && this.state.materialGUI.normalFolder) {
					try {
						this.state.materialGUI.normalFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.normalFolder = null;
					this.createNormalMaterialFolder();
				}
			}

			resetLineartParameters(forceReset = false) {
				const defaultLineartParams = {
					color: '#ffffff',
					edgeStart: 0.6,
					edgeEnd: 0.9,
					curvatureStart: 0.01,
					curvatureEnd: 0.05
				};
				
				Object.assign(this.state.materialParams.lineart, defaultLineartParams);
				this.updateLineartMaterial();
				
				if (this.state.materialMode === 'lineart' && this.state.materialGUI.lineartFolder) {
					try {
						this.state.materialGUI.lineartFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.lineartFolder = null;
					this.createLineartMaterialFolder();
				}
			}

			resetCannyParameters(forceReset = false) {
				const defaultCannyParams = {
					color: '#ffffff',
					lowThreshold: 0.1,
					highThreshold: 0.3,
					edgeStrength: 1.0,
					edgeDetail: 0.1
				};
				
				Object.assign(this.state.materialParams.canny, defaultCannyParams);
				this.updateCannyMaterial();
				
				if (this.state.materialMode === 'canny' && this.state.materialGUI.cannyFolder) {
					try {
						this.state.materialGUI.cannyFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.cannyFolder = null;
					this.createCannyMaterialFolder();
				}
			}

			resetEdgeParameters(forceReset = false) {
				const defaultEdgeParams = {
					color: '#ffffff',
					normalThreshold: 1.0,
					posThreshold: 1.0,
					edgeStart: 0.1,
					edgeEnd: 0.2,
					contrast: 2.0
				};
				
				Object.assign(this.state.materialParams.edge, defaultEdgeParams);
				this.updateEdgeMaterial();
				
				if (this.state.materialMode === 'edge' && this.state.materialGUI.edgeFolder) {
					try {
						this.state.materialGUI.edgeFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.edgeFolder = null;
					this.createEdgeMaterialFolder();
				}
			}

			resetContourParameters(forceReset = false) {
				const defaultContourParams = {
					color: '#ffffff',
					thickness: 1.5,
					depthThreshold: 0.015,
					normalThreshold: 0.4
				};
				
				Object.assign(this.state.materialParams.contour, defaultContourParams);
				this.updateContourMaterial();
				
				if (this.state.materialMode === 'contour' && this.state.materialGUI.contourFolder) {
					try {
						this.state.materialGUI.contourFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.contourFolder = null;
					this.createContourMaterialFolder();
				}
			}

			resetSSAOParameters(forceReset = false) {
				const defaultSSAOParams = {
					kernelRadius: 16,
					minDistance: 0.001,
					maxDistance: 0.05,
					output: SSAOPass.OUTPUT.Blur
				};
				
				Object.assign(this.state.postProcessingParams.ssao, defaultSSAOParams);
				
				if (this.ssaoPass) {
					this.ssaoPass.kernelRadius = defaultSSAOParams.kernelRadius;
					this.ssaoPass.minDistance = defaultSSAOParams.minDistance;
					this.ssaoPass.maxDistance = defaultSSAOParams.maxDistance;
					
					this.updateSSAOParameters();
				}
				
				if (this.state.materialMode === 'ssao' && this.state.materialGUI.ssaoFolder) {
					try {
						this.state.materialGUI.ssaoFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.ssaoFolder = null;
					this.createSSAOGUIFolder();
				}
			}

			resetGTAOParameters(forceReset = false) {
				const defaultGTAOParams = {
					radius: 0.25,
					distanceExponent: 1.0,
					thickness: 1.0,
					scale: 1.0,
					distanceFallOff: 1.0,
					samples: 16,
					output: GTAOPass.OUTPUT.Denoise
				};
				
				Object.assign(this.state.postProcessingParams.gtao, defaultGTAOParams);
				
				if (this.gtaoPass) {
					this.gtaoPass.radius = defaultGTAOParams.radius;
					this.gtaoPass.distanceExponent = defaultGTAOParams.distanceExponent;
					this.gtaoPass.thickness = defaultGTAOParams.thickness;
					this.gtaoPass.scale = defaultGTAOParams.scale;
					this.gtaoPass.distanceFallOff = defaultGTAOParams.distanceFallOff;
					this.gtaoPass.samples = defaultGTAOParams.samples;
					
					this.UpdateGTAOParameters();
				}
				
				if (this.state.materialMode === 'gtao' && this.state.materialGUI.gtaoFolder) {
					try {
						this.state.materialGUI.gtaoFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.gtaoFolder = null;
					this.createGTAOGUIFolder();
				}
			}

			handleMatChange(eOrMode) {
				const mode = typeof eOrMode === 'string' 
					? eOrMode 
					: eOrMode.target.value;
				
				this.state.materialMode = mode;
				
				// 确保后处理基础设施存在
				if (!this.composer && (mode === 'contour' || mode === 'ssao' || mode === 'gtao')) {
					this.initPostProcessing();
				}
				
				// 在非original、default和wireframe模式下关闭helper
				if (mode !== 'original' && mode !== 'default' && mode !== 'wireframe') {
					if (this.dom.toggles.helper && this.dom.toggles.helper.checked) {
						this.dom.toggles.helper.checked = false;
						this.toggleHelper();
					}
				}
				
				// 在非original、default模式下关闭阴影
				if (mode !== 'original' && mode !== 'default') {
					this.state.lights.shadowsEnabled = true;
					this.toggleShadows();
				}
				
				if (mode === 'contour') {
					// 启用轮廓模式
					this.isContourMode = true;
					
					// 确保轮廓通道启用
					if (this.contourPass) {
						this.contourPass.enabled = true;
					}
				} else {
					// 关闭轮廓模式
					this.isContourMode = false;
					
					// 禁用轮廓通道
					if (this.contourPass) {
						this.contourPass.enabled = false;
					}
				}
				
				// 确保后处理通道已初始化
				if (!this.ssaoPass && mode === 'ssao') {
					this.createSSAOPass();
				}
				if (!this.gtaoPass && mode === 'gtao') {
					this.createGTAOPass();
				}
				
				// 根据材质模式显示对应的GUI文件夹
				this.showMaterialFolder(mode);
				
				this.applyMaterialMode();
				this.updateBgColorPickerState(mode);
				this.toggleLightGUI();
			}

			applyMaterialMode() {
				const mode = this.state.materialMode;
				const side = this.getSideValue(this.state.commonParams.side);
				
				// 设置背景色
				switch (mode) {
					case 'normal':
						// (128,128,255) | (0.5,0.5,1.0)
						this.scene.background = new THREE.Color(0x8080ff);
						break;
					case 'depth':
					case 'lineart':
					case 'contour':
					case 'edge':
					case 'canny':
						this.scene.background = new THREE.Color(0x000000);
						break;
					case 'ssao':
					case 'gtao':
						this.scene.background = new THREE.Color(0xffffff);
						break;
					default:
						// 直接使用颜色选择器的当前值
						const currentBGColor = this.dom.inputs.bgColorPicker.value;
						if (currentBGColor) {
							this.scene.background = new THREE.Color(currentBGColor);
							
							// 更新状态中的背景颜色值
							if (this.state.commonParams) {
								this.state.commonParams.background = currentBGColor;
							}
						} else {
							// 默认背景色
							this.scene.background = new THREE.Color(this.state.defaultSettings.bgColor);
							this.dom.inputs.bgColorPicker.value = this.state.defaultSettings.bgColor;
							
							// 更新状态中的背景颜色值
							if (this.state.commonParams) {
								this.state.commonParams.background = this.state.defaultSettings.bgColor;
							}
						}
						break;
				}
				
				// 设置材质
				switch (mode) {
					case 'original':
						this.applyOriginalMaterials();
						break;
					case 'default':
					case 'ssao':
					case 'gtao':
						this.applyDefaultMaterial();
						break;
					case 'wireframe':
						this.applyWireframeMaterial();
						break;
					case 'normal':
					case 'contour':
						this.applyNormalMaterial();
						break;
					case 'depth':
						this.applyDepthMaterial();
						break;
					case 'lineart':
						this.applyLineArtMaterial();
						break;
					case 'edge':
						this.applyEdgeMaterial();
						break;
					case 'canny':
						this.applyCannyMaterial();
						break;
				}
				
				// 设置双面
				switch (mode) {
					case 'original':
						break;
					case 'default':
					case 'ssao':
					case 'gtao':
						this.state.materials.default.side = side;
						break;
					case 'wireframe':
						this.state.materials.wireframe.side = side;
						break;
					case 'normal':
					case 'contour':
						this.state.materials.normal.side = side;
						break;
					case 'depth':
						this.state.materials.depth.side = side;
						break;
					case 'lineart':
						this.state.materials.lineart.side = side;
						break;
					case 'edge':
						this.state.materials.edge.side = side;
						break;
					case 'canny':
						this.state.materials.canny.side = side;
						break;
				}
			}

			applyOriginalMaterials() {
				const traverse = (obj) => {
					if (obj.isMesh && this.state.originalMaterials.has(obj)) {
						const originalMaterial = this.state.originalMaterials.get(obj);
						if (originalMaterial) {
							obj.material = originalMaterial;
						}
						
						// 恢复纹理（如果启用纹理映射）
						if (this.state.textureMapping) {
							this.restoreTexturesForMesh(obj);
						}
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh && this.state.originalMaterials.has(this.state.smplMesh)) {
					const originalMaterial = this.state.originalMaterials.get(this.state.smplMesh);
					if (originalMaterial) {
						this.state.smplMesh.material = originalMaterial;
					}
				}
			}

			applyDefaultMaterial() {
				const defaultMaterial = this.createDefaultMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						// 保存原始材质（如果还没有保存）
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						
						obj.material = defaultMaterial;
						obj.material.side = this.getSideValue(this.state.commonParams.side);
					}
				};
				
				if (this.state.currentModel && this.state.currentFormat !== 'ply') {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = defaultMaterial;
					this.state.smplMesh.material.side = this.getSideValue(this.state.commonParams.side);
				}
			}

			applyWireframeMaterial() {
				const wireframeMaterial = this.createWireframeMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						// 保存原始材质（如果还没有保存）
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						// 应用线框材质
						obj.material = wireframeMaterial;
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = wireframeMaterial;
				}
			}

			applyNormalMaterial() {
				const normalMaterial = this.createNormalMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						// 保存原始材质（如果还没有保存）
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						// 应用法线材质
						obj.material = normalMaterial;
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = normalMaterial;
				}
			}

			applyDepthMaterial() {
				const depthMaterial = this.createDepthMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						// 保存原始材质（如果还没有保存）
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						// 应用深度材质
						obj.material = depthMaterial;
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = depthMaterial;
				}
			}

			applyLineArtMaterial() {
				const lineartMaterial = this.createLineArtMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						obj.material = lineartMaterial;
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = lineartMaterial;
				}
			}

			applyEdgeMaterial() {
				const edgeMaterial = this.createEdgeMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						obj.material = edgeMaterial;
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = edgeMaterial;
				}
			}

			applyCannyMaterial() {
				const cannyMaterial = this.createCannyMaterial();
				
				const traverse = (obj) => {
					if (obj.isMesh) {
						if (!this.state.originalMaterials.has(obj)) {
							this.state.originalMaterials.set(obj, obj.material);
						}
						obj.material = cannyMaterial;
					}
				};
				
				if (this.state.currentModel) {
					this.state.currentModel.traverse(traverse);
				}
				
				if (this.state.smplMesh) {
					if (!this.state.originalMaterials.has(this.state.smplMesh)) {
						this.state.originalMaterials.set(this.state.smplMesh, this.state.smplMesh.material);
					}
					this.state.smplMesh.material = cannyMaterial;
				}
			}

			getSideValue(sideString) {
				switch(sideString) {
					case 'Front': return THREE.FrontSide;
					case 'Back': return THREE.BackSide;
					case 'Double': return THREE.DoubleSide;
					default: return THREE.FrontSide;
				}
			}

			updateSceneBackground() {
				const colorValue = this.dom.inputs.bgColorPicker.value;
				const color = new THREE.Color(colorValue);
				
				// 只有在支持通用背景色的模式下才更新
				const useCommonBackground = [
					'original', 'default', 'wireframe'
				].includes(this.state.materialMode);
				
				if (useCommonBackground) {
					this.scene.background = color;
					
					if (this.state.commonParams) {
						this.state.commonParams.background = colorValue;
					}
				}
			}

			updateCommonSide() {
				const side = this.getSideValue(this.state.commonParams.side);
				
				// 更新所有材质的默认side值
				if (this.state.materialParams.default.side === 'Common') {
					this.state.materialParams.default.side = this.state.commonParams.side;
					if (this.state.materialGUI.defaultFolder) {
						this.updateDefaultMaterial();
					}
				}
			}

			saveOriginalMaterials(sceneObject) {
				sceneObject.traverse(child => {
					if (child.isMesh && !this.state.originalMaterials.has(child)) {
						// 保存材质
						this.state.originalMaterials.set(child, child.material);
						
						// 收集材质的纹理
						if (child.material) {
							this.collectTexturesFromMaterial(child.material, this.state.originalTextures, child);
						}
					}
				});
			}

			collectTexturesFromMaterial(material, textureMap, mesh) {
				// 检查传入的是否是有效材质
				if (!material) {
					console.log("Warning: Attempted to collect textures from null material");
					return;
				}
				
				// 处理数组材质（多材质）
				if (Array.isArray(material)) {
					material.forEach((mat, index) => {
						this.collectTexturesFromMaterial(mat, textureMap, mesh);
					});
					return;
				}
				
				// 定义要检查的纹理属性
				const textureProperties = [
					'map',
					'normalMap',
					'roughnessMap',
					'metalnessMap',
					'emissiveMap',
					'aoMap',
					'displacementMap',
					'alphaMap'
				];
				
				textureProperties.forEach(prop => {
					try {
						if (material[prop] && material[prop].isTexture) {
							const texture = material[prop];
							// 生成唯一键，使用网格UUID和纹理属性
							const key = mesh.uuid + '_' + prop;
							
							// 只保存一次
							if (!textureMap.has(key)) {
								textureMap.set(key, {
									texture: texture,
									property: prop,
									mesh: mesh,
									materialIndex: -1
								});
							}
						}
					} catch (error) {
						console.log("Error collecting texture property: " + prop);
					}
				});
				
				// 检查材质的 userData 中是否有额外纹理
				if (material.userData && material.userData.textures) {
					Object.keys(material.userData.textures).forEach(prop => {
						try {
							const texture = material.userData.textures[prop];
							if (texture && texture.isTexture) {
								const key = mesh.uuid + '_' + prop;
								if (!textureMap.has(key)) {
									textureMap.set(key, {
										texture: texture,
										property: prop,
										mesh: mesh,
										materialIndex: -1,
										fromUserData: true
									});
								}
							}
						} catch (error) {
							console.log("Error collecting userData texture: " + prop);
						}
					});
				}
			}

			restoreTexturesForMesh(mesh) {
				// 从原始纹理中查找这个网格的纹理
				for (const [key, textureData] of this.state.originalTextures) {
					if (textureData.mesh === mesh && mesh.material[textureData.property]) {
						try {
							// 检查纹理是否有效
							if (textureData.texture && textureData.texture.isTexture) {
								// 复制纹理
								const textureClone = textureData.texture.clone();
								mesh.material[textureData.property] = textureClone;
								mesh.material.needsUpdate = true;
							}
						} catch (error) {
							console.log("Error restoring texture for property: " + textureData.property);
						}
					}
				}
			}

			// 灯光系统
			enableSceneLights() {
				// 隐藏默认灯光
				if (this.state.lights.dir) {
					this.state.lights.dir.visible = false;
					this.state.lights.dir.castShadow = false;
				}
				if (this.state.lights.amb) {
					this.state.lights.amb.visible = false;
				}
				
				// 隐藏默认灯光的可视化
				if (this.state.lights.dir && this.state.lights.dir.userData.sphereVisualization) {
					this.state.lights.dir.userData.sphereVisualization.visible = false;
				}
				
				// 启用场景灯光
				this.state.lights.scene.forEach(light => {
					light.visible = true;
					// 根据阴影设置启用或禁用阴影
					if (this.state.lights.shadowsEnabled) {
						this.configureLightShadows(light);
					} else {
						light.castShadow = false;
					}
					
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.visible = this.dom.toggles.helper.checked;
					}
				});
				
				// 更新灯光模式状态
				this.state.useSceneLight = true;
				
				// 更新可视化可见性
				this.updateVisualizationVisibility();
			}

			createDefaultLights() {
				// 创建默认方向光
				if (!this.state.lights.dir) {
					this.state.lights.dir = new THREE.DirectionalLight(
						new THREE.Color(this.state.lights.dirColor), 
						this.state.defaultSettings.dirLight
					);
					this.state.lights.dir.name = "DefaultDirectionalLight";
					
					// 设置位置和方向
					this.updateDirLightFromSpherical();
					this.state.lights.dir.target.position.set(0, 0, 0);
					
					// 根据阴影设置配置阴影
					if (this.state.lights.shadowsEnabled && !this.state.useSceneLight) {
						this.state.lights.dir.castShadow = true;
						this.configureLightShadows(this.state.lights.dir);
					} else {
						this.state.lights.dir.castShadow = false;
					}
					
					this.scene.add(this.state.lights.dir);
					this.scene.add(this.state.lights.dir.target);
					
					// 添加到默认灯光数组
					this.state.lights.default.push(this.state.lights.dir);
				}
				
				// 创建默认环境光
				if (!this.state.lights.amb) {
					this.state.lights.amb = new THREE.AmbientLight(
						new THREE.Color(this.state.lights.ambColor), 
						this.state.defaultSettings.ambLight
					);
					this.state.lights.amb.name = "DefaultAmbientLight";
					this.scene.add(this.state.lights.amb);
					
					// 添加到默认灯光数组
					this.state.lights.default.push(this.state.lights.amb);
				}
			}

			enableDefaultLights() {
				// 隐藏场景灯光
				this.state.lights.scene.forEach(light => {
					light.visible = false;
					light.castShadow = false;
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.visible = false;
					}
				});
				
				// 启用默认灯光
				if (this.state.lights.dir) {
					this.state.lights.dir.visible = true;
					// 根据阴影设置启用或禁用阴影
					if (this.state.lights.shadowsEnabled) {
						this.state.lights.dir.castShadow = true;
						this.state.lights.dir.shadow.needsUpdate = true;
					} else {
						this.state.lights.dir.castShadow = false;
					}
				}
				
				if (this.state.lights.amb) {
					this.state.lights.amb.visible = true;
				}
				
				// 确保默认灯光在 default 数组中
				if (!this.state.lights.default.includes(this.state.lights.dir)) {
					this.state.lights.default.push(this.state.lights.dir);
				}
				if (!this.state.lights.default.includes(this.state.lights.amb)) {
					this.state.lights.default.push(this.state.lights.amb);
				}
				
				// 为方向光创建或更新可视化
				if (this.state.lights.dir) {
					// 如果已有可视化，更新位置；否则创建新可视化
					if (this.state.lights.dir.userData.sphereVisualization) {
						// 更新现有可视化位置
						this.state.lights.dir.userData.sphereVisualization.position.copy(this.state.lights.dir.position);
						this.state.lights.dir.userData.sphereVisualization.visible = this.dom.toggles.helper.checked;
					} else {
						this.createLightVisualization(this.state.lights.dir);
					}
				}
				
				// 更新灯光模式状态
				this.state.useSceneLight = false;
				
				// 更新可视化可见性
				this.updateVisualizationVisibility();
			}

			adjustDefaultDirLightForScene() {
				const dirLight = this.state.lights.dir;
				const aggregatedData = this.getAggregatedBBoxData();
				
				if (!dirLight || !dirLight.isDirectionalLight || dirLight.name !== "DefaultDirectionalLight") {
					return;
				}
				
				let boxSize;
				let sceneCenter;
				
				if (!aggregatedData || !aggregatedData.overallSize || aggregatedData.overallSize.lengthSq() === 0) {
					// 如果没有汇总数据，使用单帧
					const sceneBBox = this.state.sceneBBox;
					sceneCenter = this.state.sceneCenter;
					
					if (!sceneBBox || sceneBBox.isEmpty() || !sceneCenter) {
						return;
					}
					
					// 计算场景尺寸
					boxSize = new THREE.Vector3();
					sceneBBox.getSize(boxSize);
					
				} else {
					boxSize = aggregatedData.overallSize;
					sceneCenter = aggregatedData.averageCenter;
				}
				
				// 保存场景中心
				this.state.sceneCenter = sceneCenter.clone();
				
				// 计算最大维度，用于确定灯光距离和阴影范围
				const maxDimension = parseFloat((Math.max(boxSize.x, boxSize.y, boxSize.z)).toFixed(2));
				
				// 1. 计算合适的灯光距离（保持当前比例或使用场景尺寸）
				this.state.lights.dirSpherical.radius = maxDimension;
				
				// 2. 更新灯光位置（基于球面坐标）
				this.updateDirLightFromSpherical();
				
				// 3. 调整阴影相机参数
				const shadowCamera = dirLight.shadow.camera;
				const margin = 1.2; // 20%边界
				const shadowRange = parseFloat((maxDimension * 1.72 / 2 * margin).toFixed(2));
				
				// 更新状态中的值
				this.state.lights.shadowSettings.camera.left = -shadowRange;
				this.state.lights.shadowSettings.camera.right = shadowRange;
				this.state.lights.shadowSettings.camera.top = shadowRange;
				this.state.lights.shadowSettings.camera.bottom = -shadowRange;
				
				// 4. 调整近远裁剪面
				const nearClip = Math.max(0.1, maxDimension * 0.01);
				const farClip = maxDimension * 3;
				this.state.lights.shadowSettings.camera.near = nearClip;
				this.state.lights.shadowSettings.camera.far = farClip;
				
				// 5. 更新球面坐标显示
				this.updateSphericalFromDirLight();
				
				// 6. 灯光设置
				dirLight.castShadow = this.state.lights.shadowsEnabled;
				this.updateShadowSettings();
				
				// 7. 更新灯光可视化位置
				if (dirLight.userData.sphereVisualization) {
					dirLight.userData.sphereVisualization.position.copy(dirLight.position);
				}
				
				// 8. 更新GUI控件的值
				this.createLightGUI();
			}

			configureLightShadows(light) {
				if (!light || !light.isLight) return;
				
				// 根据灯光类型配置阴影
				if (light.isDirectionalLight) {
					light.castShadow = true;
					light.shadow.mapSize.width = this.state.lights.shadowSettings.mapSize;
					light.shadow.mapSize.height = this.state.lights.shadowSettings.mapSize;
					light.shadow.radius = this.state.lights.shadowSettings.radius;
					light.shadow.blurSamples = this.state.lights.shadowSettings.samples;
					light.shadow.bias = this.state.lights.shadowSettings.bias;
					/* light.shadow.normalBias = this.state.lights.shadowSettings.normalBias; */
					light.shadow.camera.near = this.state.lights.shadowSettings.camera.near;
					light.shadow.camera.far = this.state.lights.shadowSettings.camera.far;
					light.shadow.camera.left = this.state.lights.shadowSettings.camera.left;
					light.shadow.camera.right = this.state.lights.shadowSettings.camera.right;
					light.shadow.camera.top = this.state.lights.shadowSettings.camera.top;
					light.shadow.camera.bottom = this.state.lights.shadowSettings.camera.bottom;
					
					// 更新阴影相机矩阵
					light.shadow.camera.updateProjectionMatrix();
					
				} else if (light.isSpotLight) {
					light.castShadow = true;
					light.shadow.mapSize.width = this.state.lights.shadowSettings.mapSize;
					light.shadow.mapSize.height = this.state.lights.shadowSettings.mapSize;
					light.shadow.radius = this.state.lights.shadowSettings.radius;
					light.shadow.blurSamples = this.state.lights.shadowSettings.samples;
					light.shadow.bias = this.state.lights.shadowSettings.bias;
					/* light.shadow.normalBias = this.state.lights.shadowSettings.normalBias; */
					
				} else if (light.isPointLight) {
					light.castShadow = true;
					light.shadow.mapSize.width = this.state.lights.shadowSettings.mapSize;
					light.shadow.mapSize.height = this.state.lights.shadowSettings.mapSize;
					light.shadow.radius = this.state.lights.shadowSettings.radius;
					light.shadow.blurSamples = this.state.lights.shadowSettings.samples;
					light.shadow.bias = this.state.lights.shadowSettings.bias * 0.1;
				}
				
				// 更新阴影贴图
				light.shadow.needsUpdate = true;
			}

			processSceneLights(scene) {
				// 清理旧灯光
				this.state.lights.scene.forEach(light => {
					if (light.userData.sphereVisualization) {
						this.scene.remove(light.userData.sphereVisualization);
					}
					this.scene.remove(light);
				});
				this.state.lights.scene = [];
				
				// 收集所有灯光
				const sceneLights = [];
				scene.traverse(child => { 
					if (child.isLight) { 
						sceneLights.push(child);
					} 
				});
				
				// 处理每个灯光
				sceneLights.forEach(light => {
					// 确保userData存在
					if (!light.userData) light.userData = {};
					
					// 标记为场景灯光
					light.userData.isSceneLight = true;
					
					// 如果使用场景灯光且阴影启用，配置阴影
					if (this.state.useSceneLight && this.state.lights.shadowsEnabled) {
						this.configureLightShadows(light);
					} else {
						light.castShadow = false;
					}
					
					// 创建灯光可视化
					this.createLightVisualization(light);
					
					// 添加到场景灯光列表
					this.state.lights.scene.push(light);
					
					// 初始可见性由灯光模式决定
					light.visible = this.state.useSceneLight;
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.visible = this.state.useSceneLight && this.dom.toggles.helper.checked;
					}
				});
				
				this.updateDirLightIntensity(); 
				this.updateAmbLightIntensity();
				
				// 如果当前使用场景灯光模式，启用它们
				if (this.state.useSceneLight) {
					this.enableSceneLights();
				}
			}

			// 材质灯光界面
			resetSettings() {
				// 重置材质
				this.state.materialMode = 'original';
				if (this.dom.inputs.materialSelect) {
					this.dom.inputs.materialSelect.value = 'original';
				}
				
				this.resetDefaultParameters();
				this.resetWireframeParameters();
				this.resetNormalParameters();
				this.resetLineartParameters();
				this.resetCannyParameters();
				this.resetEdgeParameters();
				this.resetContourParameters();
				this.resetSSAOParameters();
				this.resetGTAOParameters();
				
				this.dom.inputs.bgColorPicker.value = this.state.defaultSettings.bgColor;
				this.handleMatChange('original');
				this.disposeMaterialCache();
				
				// 重置灯光
				this.state.useSceneLight = true;
				this.state.lights.shadowsEnabled = true;
				this.toggleLightMode();
				this.toggleShadows();
				
				this.resetDirLightParameters();
				this.resetAmbLightParameters();
				
				// 重置辅助工具缩放比例为默认值 1.0
				this.state.helperSize = 1.0;
				
				// 更新UI滑块值
				if (this.dom.inputs.helperSize) {
					this.dom.inputs.helperSize.value = "1.00";
				}
				
				// 更新所有可视化辅助工具的大小
				this.updateAllVisualizationSizes();
				
				if (this.dom.toggles.helper) {
					this.dom.toggles.helper.checked = true;
					this.toggleHelper();
				}
				
				if (this.dom.toggles.info) {
					this.dom.toggles.info.checked = true;
					this.toggleInfoDisplay();
				}
			}

			updateMaterialSide(e) {
				const sideValue = e.target.value;
				this.state.commonParams.side = sideValue;
				const side = this.getSideValue(sideValue);
				
				// 1. 更新所有单例材质
				const materials = [
					this.state.materials.default,
					this.state.materials.normal,
					this.state.materials.depth,
					this.state.materials.wireframe,
					this.state.materials.lineart,
					this.state.materials.edge,
					this.state.materials.canny
				];
				
				materials.forEach(material => {
					if (material) {
						material.side = side;
						material.needsUpdate = true;
					}
				});
				
				// 2. 更新所有场景材质
				this.state.originalMaterials.forEach((material) => {
					if (!material) return;
					
					// 处理数组材质
					if (Array.isArray(material)) {
						material.forEach(mat => {
							if (mat && mat.isMaterial && mat.side !== side) {
								mat.side = side;
								mat.needsUpdate = true;
							}
						});
					} 
					// 处理单个材质
					else if (material.isMaterial && material.side !== side) {
						material.side = side;
						material.needsUpdate = true;
					}
				});
				
				// 3. 重新应用当前材质模式
				this.applyMaterialMode();
			}

			updateBgColorPickerState(mode) {
				const bgColorPicker = this.dom.inputs.bgColorPicker;
				
				// 只在original, default, wireframe模式下启用BG颜色选择器
				const enableBGColor = (mode === 'original' || mode === 'default' || mode === 'wireframe');
				
				if (enableBGColor) {
					bgColorPicker.disabled = false;
					bgColorPicker.classList.remove('disabled-control');
					bgColorPicker.classList.add('enabled-control');
				} else {
					bgColorPicker.disabled = true;
					bgColorPicker.classList.add('disabled-control');
					bgColorPicker.classList.remove('enabled-control');
				}
			}

			toggleLightMode() {
				this.state.useSceneLight = !this.state.useSceneLight;
				
				const { dirLight, ambLight } = this.dom.inputs;
				const lightLabel = this.dom.labels.lightLabel;
				const lightToggle = this.dom.toggles.light;
				
				if (this.state.useSceneLight) {
					// 场景灯光模式
					lightLabel.textContent = "Scene Light";
					this.enableSceneLights();
				} else {
					// 默认灯光模式
					lightLabel.textContent = "Default Light";
					this.enableDefaultLights();
				}
				
				// 同步复选框状态
				lightToggle.checked = this.state.useSceneLight;
				lightToggle.classList.remove('disabled-control');
				lightToggle.classList.add('enabled-control');
				
				this.toggleLightGUI();
			}

			toggleShadows() {
				this.state.lights.shadowsEnabled = !this.state.lights.shadowsEnabled;
				
				// 更新渲染器阴影设置
				this.renderer.shadowMap.enabled = this.state.lights.shadowsEnabled;
				
				// 根据当前灯光模式更新相应灯光的阴影
				if (this.state.useSceneLight) {
					// 场景灯光模式：更新所有场景灯光的阴影
					this.state.lights.scene.forEach(light => {
						if (light.isDirectionalLight || light.isSpotLight || light.isPointLight) {
							if (this.state.lights.shadowsEnabled) {
								this.configureLightShadows(light);
							} else {
								light.castShadow = false;
							}
						}
					});
					
					// 确保默认方向光阴影关闭
					if (this.state.lights.dir) {
						this.state.lights.dir.castShadow = false;
					}
				} else {
					// 默认灯光模式：更新默认方向光的阴影
					if (this.state.lights.dir) {
						this.state.lights.dir.castShadow = this.state.lights.shadowsEnabled;
						this.state.lights.dir.shadow.needsUpdate = true;
					}
					
					// 确保场景灯光阴影关闭
					this.state.lights.scene.forEach(light => {
						light.castShadow = false;
					});
				}
				
				// 更新所有模型的阴影设置
				const updateModelShadows = (model) => {
					if (model && model.traverse) {
						model.traverse(child => {
							if (child.isMesh) {
								child.castShadow = this.state.lights.shadowsEnabled;
								child.receiveShadow = this.state.lights.shadowsEnabled;
							}
						});
					}
				};
				
				// 更新主模型
				updateModelShadows(this.state.currentModel);
				
				// 更新SMPL模型
				if (this.state.smplMesh) {
					this.state.smplMesh.castShadow = this.state.lights.shadowsEnabled;
					this.state.smplMesh.receiveShadow = this.state.lights.shadowsEnabled;
				}
				
				// 更新按钮状态
				this.updateShadowsButtonState();
			}

			updateShadowsButtonState() {
				const shadowsToggle = this.dom.toggles.shadows;
				if (!shadowsToggle) return;
				
				// 设置复选框状态
				shadowsToggle.checked = this.state.lights.shadowsEnabled;
			}

			updateDirLightColor() {
				if (this.state.lights.dir) {
					this.state.lights.dir.color.set(this.state.lights.dirColor);
				}
			}

			updateAmbLightColor() {
				if (this.state.lights.amb) {
					this.state.lights.amb.color.set(this.state.lights.ambColor);
				}
			}

			updateDirLightIntensity() {
				if (!this.state.useSceneLight && this.state.lights.dir) {
					this.state.lights.dir.intensity = this.state.lights.dirIntensity;
				}
			}

			updateAmbLightIntensity() {
				if (!this.state.useSceneLight && this.state.lights.amb) {
					this.state.lights.amb.intensity = this.state.lights.ambIntensity;
				}
			}

			updateDirLightFromSpherical() {
				if (!this.state.lights.dir || !this.state.sceneCenter) return;
				
				const spherical = this.state.lights.dirSpherical;
				
				// 将角度转换为弧度
				const phi = THREE.MathUtils.degToRad(90 - spherical.elevation);
				const theta = THREE.MathUtils.degToRad(spherical.azimuth);
				
				// 计算球面坐标到笛卡尔坐标
				const x = spherical.radius * Math.sin(phi) * Math.cos(theta);
				const y = spherical.radius * Math.cos(phi);
				const z = spherical.radius * Math.sin(phi) * Math.sin(theta);
				
				// 设置灯光位置（相对场景中心）
				const targetPos = this.state.sceneCenter || new THREE.Vector3(0, 0, 0);
				this.state.lights.dir.position.set(
					targetPos.x + x,
					targetPos.y + y,
					targetPos.z + z
				);
				
				// 更新灯光目标
				this.state.lights.dir.target.position.copy(targetPos);
				
				// 更新灯光可视化
				if (this.state.lights.dir.userData.sphereVisualization) {
					this.state.lights.dir.userData.sphereVisualization.position.copy(this.state.lights.dir.position);
				}
			}

			updateSphericalFromDirLight() {
				if (!this.state.lights.dir || !this.state.sceneCenter) return;
				
				const targetPos = this.state.sceneCenter || new THREE.Vector3(0, 0, 0);
				const lightPos = this.state.lights.dir.position;
				
				// 计算相对位置
				const relative = new THREE.Vector3().subVectors(lightPos, targetPos);
				
				// 转换为球面坐标
				const spherical = new THREE.Spherical();
				spherical.setFromVector3(relative);
				
				// 转换为角度
				this.state.lights.dirSpherical.radius = parseFloat((spherical.radius).toFixed(2));
				this.state.lights.dirSpherical.azimuth = parseFloat((THREE.MathUtils.radToDeg(spherical.theta)).toFixed(2));
				this.state.lights.dirSpherical.elevation = parseFloat((90 - THREE.MathUtils.radToDeg(spherical.phi)).toFixed(2));
				
				// 确保方位角在0-360度范围内
				if (this.state.lights.dirSpherical.azimuth < 0) {
					this.state.lights.dirSpherical.azimuth += 360;
				}
			}

			updateShadowType() {
				const shadowType = this.state.lights.shadowSettings.shadowTypes[this.state.lights.shadowSettings.shadowType];
				if (shadowType && this.renderer) {
					this.renderer.shadowMap.type = shadowType;
				}
			}

			updateShadowSettings() {
				if (!this.state.lights.dir) return;
				
				const dirLight = this.state.lights.dir;
				const settings = this.state.lights.shadowSettings;
				
				// 更新阴影贴图大小
				dirLight.shadow.mapSize.width = settings.mapSize;
				dirLight.shadow.mapSize.height = settings.mapSize;
				
				// 更新阴影半径和采样
				dirLight.shadow.radius = settings.radius;
				if (dirLight.shadow.blurSamples !== undefined) {
					dirLight.shadow.blurSamples = settings.samples;
				}
				
				// 更新阴影偏移
				dirLight.shadow.bias = settings.bias;
				dirLight.shadow.normalBias = settings.normalBias;
				
				// 更新阴影相机参数
				const shadowCam = dirLight.shadow.camera;
				shadowCam.near = settings.camera.near;
				shadowCam.far = settings.camera.far;
				shadowCam.left = settings.camera.left;
				shadowCam.right = settings.camera.right;
				shadowCam.top = settings.camera.top;
				shadowCam.bottom = settings.camera.bottom;
				shadowCam.updateProjectionMatrix();
				
				// 同时更新场景灯光的阴影设置
				this.state.lights.scene.forEach(light => {
					if (light.castShadow) {
						this.configureLightShadows(light);
					}
				});
			}

			resetDirLightParameters(resetType = 'all') {
				const defaultMainParams = {
					dirColor: '#ffffff',
					dirIntensity: 2.5
				};
				
				const defaultPoseParams = {
					dirSpherical: {
						radius: 5,
						azimuth: 45,
						elevation: 45
					}
				};
				
				const defaultShadowParams = {
					shadowType: 'pcfsoft',
					mapSize: 2048,
					radius: 4,
					samples: 8,
					bias: -0.0001,
					normalBias: 0.01,
					camera: {
						near: 0.1,
						far: 10,
						left: -5,
						right: 5,
						top: 5,
						bottom: -5
					}
				};
				
				// 根据参数类型重置
				const resetTypes = resetType.toLowerCase().split(',').map(t => t.trim());
				
				resetTypes.forEach(type => {
					switch(type) {
						case 'main':
							// 重置颜色和强度
							this.state.lights.dirColor = defaultMainParams.dirColor;
							this.state.lights.dirIntensity = defaultMainParams.dirIntensity;
							this.updateDirLightColor();
							this.updateDirLightIntensity();
							break;
							
						case 'pose':
							// 重置球面坐标
							Object.assign(this.state.lights.dirSpherical, defaultPoseParams.dirSpherical);
							this.updateDirLightFromSpherical();
							break;
							
						case 'shadow':
							// 重置阴影设置
							Object.assign(this.state.lights.shadowSettings, defaultShadowParams);
							this.updateShadowType();
							this.updateShadowSettings();
							break;
							
						case 'all':
							// 重置所有
							this.resetDirLightParameters('main,pose,shadow');
							break;
					}
				});
				
				// 重建GUI文件夹
				if (this.state.lightGUI.dirLightFolder && this.state.lightGUI.ambLightFolder) {
					try {
						this.state.lightGUI.dirLightFolder.destroy();
						this.state.lightGUI.ambLightFolder.destroy();
					} catch(e) {}
					this.state.lightGUI.dirLightFolder = null;
					this.state.lightGUI.ambLightFolder = null;
					this.createDirLightFolder();
					this.createAmbLightFolder();
				}
			}

			resetAmbLightParameters() {
				const defaultAmbParams = {
					ambColor: '#ffffff',
					ambIntensity: 0.6
				};
				
				// 更新状态
				this.state.lights.ambColor = defaultAmbParams.ambColor;
				this.state.lights.ambIntensity = defaultAmbParams.ambIntensity;
				
				// 应用更新
				this.updateAmbLightColor();
				this.updateAmbLightIntensity();
				
				// 重建GUI文件夹
				if (this.state.lightGUI.dirLightFolder && this.state.lightGUI.ambLightFolder) {
					try {
						this.state.lightGUI.dirLightFolder.destroy();
						this.state.lightGUI.ambLightFolder.destroy();
					} catch(e) {}
					this.state.lightGUI.dirLightFolder = null;
					this.state.lightGUI.ambLightFolder = null;
					this.createDirLightFolder();
					this.createAmbLightFolder();
				}
			}

			// 相机系统
			applyRotationCorrection(object, objectType = 'camera') {
				const objectName = object.name;
				const rotationBefore = object.rotation.clone();
				const quaternionBefore = object.quaternion.clone();
				
				const correctionQuaternion = new THREE.Quaternion();
				correctionQuaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), -Math.PI/2);
				object.quaternion.multiply(correctionQuaternion);
				object.rotation.setFromQuaternion(object.quaternion);
				
				const rotationAfter = object.rotation.clone();
				
				object.userData.fbxCorrectionQuaternion = correctionQuaternion.clone();
				object.userData.appliedRotationCorrection = true;
				return object;
			}

			applyLookAt(object, targetPosition, objectType = 'camera', options = {}) {
				const { updateMatrixWorld = true, onlyCalculate = false } = options;
				const objectName = object.name;
				const rotationBefore = object.rotation.clone();
				const direction = new THREE.Vector3().subVectors(targetPosition, object.position).normalize();
				
				// 根据对象类型创建临时对象来计算旋转
				let tempObject;
				
				if (objectType === 'camera') {
					tempObject = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
				} else if (objectType === 'light') {
					// 对于灯光，使用Object3D来计算旋转
					tempObject = new THREE.Object3D();
				} else {
					tempObject = new THREE.Object3D();
				}
				
				// 复制位置和上方向
				tempObject.position.copy(object.position);
				tempObject.up.set(0, 1, 0);
				
				// 应用lookAt
				tempObject.lookAt(targetPosition);
				
				// 记录应用后的旋转
				const rotationAfter = tempObject.rotation.clone();
				
				// 如果不是只计算，则应用到原对象
				if (!onlyCalculate) {
					object.quaternion.copy(tempObject.quaternion);
					object.rotation.copy(rotationAfter);
					
					// 对于灯光，如果是聚光灯或平行光，设置target属性
					if (objectType === 'light' && (object.isSpotLight || object.isDirectionalLight)) {
						if (!object.target) {
							object.target = new THREE.Object3D();
							if (object.parent) {
								object.parent.add(object.target);
							}
						}
						object.target.position.copy(targetPosition);
					}
					
					// 根据需要更新矩阵
					if (updateMatrixWorld) {
						object.updateMatrix();
						object.updateMatrixWorld(true);
					}
				}
				
				// 清理临时对象
				tempObject.geometry?.dispose();
				tempObject.material?.dispose();
				
				return {
					direction: direction,
					rotation: rotationAfter,
					quaternion: tempObject.quaternion.clone(),
					targetPosition: targetPosition.clone()
				};
			}

			applyRollAngle() {
				// 只对默认相机和自定义相机有效
				if (this.state.cameras.currentType !== 'default' && this.state.cameras.currentType !== 'custom') {
					return;
				}
				
				const input = this.dom.inputs.rollAngle;
				if (!input) return;
				
				const value = parseFloat(input.value);
				
				if (value < -180 || value > 180) {
					const clampedValue = Math.max(-180, Math.min(180, value));
					input.value = clampedValue.toFixed(2);
					return;
				}
				
				this.applyRollAngleToCamera(this.camera, value, true);
				this.controls.update();
				this.saveCurrentCameraState();
			}

			applyRollAngleToCamera(camera, targetRollDegrees, forceApply) {
				if (!camera) return;
				
				// 确保是默认相机或自定义相机
				if (this.state.cameras.currentType !== 'default' && this.state.cameras.currentType !== 'custom') {
					return;
				}
				
				// roll角度变化过小，不需要更新，避免orbit control异常
				const currentRoll = camera.userData.rollAngle || 0;
				if (!forceApply && Math.abs(currentRoll - targetRollDegrees) < 0.01) {
					return;
				}
				
				// 保存目标 roll 角度到相机 userData
				camera.userData.rollAngle = targetRollDegrees;
				
				// 获取当前相机的方向（从相机指向目标点）
				const direction = new THREE.Vector3();
				direction.subVectors(this.controls.target, camera.position).normalize();
				
				// 计算一个与方向垂直的参考 up 向量（初始 up）
				// 如果方向接近垂直（与 (0,1,0) 点积接近 1 或 -1），则使用 (0,0,1) 作为参考
				let referenceUp = new THREE.Vector3(0, 1, 0);
				const dot = Math.abs(direction.dot(referenceUp));
				if (dot > 0.99) {
					referenceUp = new THREE.Vector3(0, 0, 1);
				}
				
				// 计算参考右向量（与方向和参考 up 垂直）
				const referenceRight = new THREE.Vector3();
				referenceRight.crossVectors(direction, referenceUp).normalize();
				
				// 重新计算垂直的参考 up 向量
				const verticalUp = new THREE.Vector3();
				verticalUp.crossVectors(referenceRight, direction).normalize();
				
				// 计算 roll 弧度
				const rollRadians = targetRollDegrees * Math.PI / 180;
				
				// 创建 roll 旋转四元数（绕方向轴旋转）
				const rollQuaternion = new THREE.Quaternion();
				rollQuaternion.setFromAxisAngle(direction, rollRadians);
				
				// 应用 roll 旋转到垂直的 up 向量，得到目标 up 向量
				const targetUp = verticalUp.clone();
				targetUp.applyQuaternion(rollQuaternion);
				targetUp.normalize();
				
				// 设置新的 up 向量
				camera.up.copy(targetUp);
				camera.userData.upVector = targetUp.clone();
				
				// 确保相机仍然看向目标点
				camera.lookAt(this.controls.target);
			}

			calculateCameraRollAngle(camera, targetPosition = null, fixYup = true) {
				if (!camera) return { roll: 0, upVector: new THREE.Vector3(0, 1, 0) };
				
				try {
					// 获取相机的当前旋转四元数
					const quaternion = camera.quaternion.clone();
					
					// 计算相机的局部坐标轴
					const localZ = new THREE.Vector3(0, 0, 1).applyQuaternion(quaternion).normalize();
					const localY = new THREE.Vector3(0, 1, 0).applyQuaternion(quaternion).normalize();
					// const localX = new THREE.Vector3(1, 0, 0).applyQuaternion(quaternion).normalize();
					
					// 确定相机的朝向向量
					let lookDirection;
					if (targetPosition) {
						// 目标相机：朝向目标点，look dir不一定是local -z
						lookDirection = new THREE.Vector3().subVectors(targetPosition, camera.position).normalize();
					} else {
						// 自由相机：使用局部-Z轴
						lookDirection = localZ.clone().negate();
					}
					
					// 选择参考上向量：优先世界+Y，如果接近平行则使用世界+X或+Z
					let referenceUp = this.getPerpendicularUpVector(lookDirection, 0.99);
					
					// 确保参考上向量与朝向垂直
					const proj = referenceUp.dot(lookDirection);
					referenceUp.sub(lookDirection.clone().multiplyScalar(proj)).normalize();
					
					// 计算当前上向量在垂直于朝向的平面上的投影
					// 对于自由相机，直接使用 localY；对于目标相机，投影到垂直平面
					let currentUpProjection;
					if (!targetPosition) {
						// 自由相机：直接使用 localY
						currentUpProjection = localY.clone();
					} else {
						// 目标相机：需要投影
						currentUpProjection = localY.clone();
						const upDotLook = currentUpProjection.dot(lookDirection);
						// 只有不垂直时才需要投影
						if (Math.abs(upDotLook) > 0.001) {
							currentUpProjection.sub(lookDirection.clone().multiplyScalar(upDotLook));
						}
						currentUpProjection.normalize();
					}
					
					// 安全检查
					if (currentUpProjection.length() < 0.001 || referenceUp.length() < 0.001) {
						const upVector = fixYup ? new THREE.Vector3(0, 1, 0) : localY.clone();
						return { roll: 0, upVector };
					}
					
					// 计算两个投影向量的夹角
					const dot = Math.max(-1.0, Math.min(1.0, currentUpProjection.dot(referenceUp)));
					let angle = Math.acos(dot);
					
					// 确定角度方向（正负）
					const cross = new THREE.Vector3().crossVectors(referenceUp, currentUpProjection);
					if (cross.dot(lookDirection) < 0) {
						angle = -angle;
					}
					
					// 转换为角度并规范化
					const rollAngle = THREE.MathUtils.radToDeg(angle);
					const normalizedRoll = ((rollAngle + 180) % 360) - 180;
					
					// 根据 fixYup 参数决定返回哪个 upVector
					let resultUpVector;
					if (fixYup && Math.abs(normalizedRoll) < 0.001) {
						// 如果 roll 为 0 且 fixYup 为 true，返回世界 +Y
						resultUpVector = new THREE.Vector3(0, 1, 0);
					} else {
						// 否则返回相机的局部 Y 轴
						resultUpVector = localY.clone();
					}
					
					return {
						roll: normalizedRoll,
						upVector: currentUpProjection.clone()
					};
				} catch (error) {
					return { roll: 0, upVector: new THREE.Vector3(0, 1, 0) };
				}
			}

			calculateViewHeightFromFov(fovDegrees, distance) {
				const fovRadians = THREE.MathUtils.degToRad(fovDegrees);
				// 计算：2 * 距离 * tan(fov/2)
				const viewHeight = 2 * distance * Math.tan(fovRadians / 2);
				return Math.max(0.01, viewHeight);
			}

			calculateFovFromViewHeight(viewHeight, distance) {
				if (distance <= 0) return 4;
				
				// 计算：2 * arctan(viewHeight / (2 * distance))
				const fovRadians = 2 * Math.atan2(viewHeight / 2, distance);
				const fovDegrees = THREE.MathUtils.radToDeg(fovRadians);
				return Math.max(0.01, Math.min(179.99, fovDegrees));
			}

			getPerpendicularUpVector(lookDirection, threshold = 0.999, axesPriority = null) {
				const normalizedLook = lookDirection.clone().normalize();
				
				// 默认y->x->z
				const defaultAxes = [
					new THREE.Vector3(0, 1, 0),
					new THREE.Vector3(1, 0, 0),
					new THREE.Vector3(0, 0, 1)
				];
				
				const axes = axesPriority || defaultAxes;
				
				for (const axis of axes) {
					const dotValue = Math.abs(normalizedLook.dot(axis));
					if (dotValue <= threshold) {
						return axis.clone();
					}
				}
				
				return new THREE.Vector3(0, 1, 0);
			}

			alignVectorToAxis(vector, threshold = 0.999, axesPriority = null) {
				// 默认y->x->z
				const defaultAxes = [
					new THREE.Vector3(0, 1, 0),
					new THREE.Vector3(1, 0, 0),
					new THREE.Vector3(0, 0, 1)
				];
				
				const axes = axesPriority || defaultAxes;
				
				if (vector.lengthSq() < 0.0001) {
					return axes[0].clone();
				}
				
				const normalizedVector = vector.clone().normalize();
				
				for (const axis of axes) {
					const dotValue = Math.abs(normalizedVector.dot(axis));
					if (dotValue > threshold) {
						return axis.clone();
					}
				}
				
				return normalizedVector;
			}

			resetYup() {
				this.camera.up.set(0,1,0);
				this.dom.inputs.rollAngle.value = "0.00";
				this.controls.update();
			}

			// BBox & Center & Focus
			initAnimationBBoxData() {
				const totalFrames = this.state.playback.totalFrames;
				const animationBBoxData = this.state.animationBBoxData;
				
				// 重置数据
				animationBBoxData.sampledFrames.clear();
				animationBBoxData.cachedFrames.clear();
				animationBBoxData.sampleFrameNumbers = [];
				animationBBoxData.hasAnimation = totalFrames > 1;
				animationBBoxData.isInitialized = false;
				
				if (totalFrames <= 1) {
					// 无动画场景：只采样第一帧
					const bboxData = this.getBBoxForFrame(0);
					animationBBoxData.sampledFrames.set(0, bboxData);
					animationBBoxData.sampleFrameNumbers.push(0);
					
					// 汇总数据就是这一帧的数据
					animationBBoxData.aggregated = {
						overallMin: bboxData.min.clone(),
						overallMax: bboxData.max.clone(),
						averageCenter: bboxData.center.clone(),
						overallSize: bboxData.size.clone()
					};
					
					animationBBoxData.isInitialized = true;
				} else {
					// 有动画场景：启动动态采样
					this.sampleAnimationBBoxData();
				}
			}

			getAggregatedBBoxData() {
				const animationBBoxData = this.state.animationBBoxData;
				
				// 如果系统未初始化，先初始化
				if (!animationBBoxData.isInitialized) {
					this.initAnimationBBoxData();
				}
				
				return animationBBoxData.aggregated;
			}

			sampleAnimationBBoxData() {
				const totalFrames = this.state.playback.totalFrames;
				const samplingInterval = this.state.animationBBoxData.samplingInterval;
				
				if (totalFrames <= 1) {
					return; // 静态场景已在init中处理
				}
				
				// 计算采样帧号
				const sampleFrameNumbers = [];
				for (let frame = 0; frame < totalFrames; frame += samplingInterval) {
					sampleFrameNumbers.push(frame);
				}
				
				// 确保最后一帧被包含
				const lastFrame = totalFrames - 1;
				if (!sampleFrameNumbers.includes(lastFrame)) {
					sampleFrameNumbers.push(lastFrame);
				}
				
				// 对采样帧号排序
				sampleFrameNumbers.sort((a, b) => a - b);
				
				// 批量计算采样帧的包围盒
				const sampledFrames = new Map();
				const overallMin = new THREE.Vector3(Infinity, Infinity, Infinity);
				const overallMax = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
				const centerSum = new THREE.Vector3(0, 0, 0);
				
				sampleFrameNumbers.forEach((frame, index) => {
					const bboxData = this.getBBoxForFrame(frame);
					sampledFrames.set(frame, bboxData);
					
					// 更新汇总数据
					overallMin.min(bboxData.min);
					overallMax.max(bboxData.max);
					centerSum.add(bboxData.center);
					
					// 更新采样进度
					this.state.animationBBoxData.sampledFrames.set(frame, bboxData);
					this.state.animationBBoxData.sampleFrameNumbers = sampleFrameNumbers;
				});
				
				// 计算最终汇总数据
				const count = sampleFrameNumbers.length;
				this.state.animationBBoxData.aggregated = {
					overallMin,
					overallMax,
					averageCenter: centerSum.divideScalar(count),
					overallSize: new THREE.Vector3().subVectors(overallMax, overallMin)
				};
				
				this.state.animationBBoxData.isInitialized = true;
				this.state.animationBBoxData.sampledFrames = sampledFrames;
			}

			getBBoxForFrame(targetFrame) {
				// 保存当前状态
				const originalFrame = this.state.playback.currentFrame;
				
				try {
					// 使用 updateVisualsToFrame 更新到目标帧
					this.updateVisualsToFrame(targetFrame, true);
					
					// 计算当前状态下的包围盒
					const box = this.getBBox();
					
					if (!box.isEmpty()) {
						const center = new THREE.Vector3();
						const size = new THREE.Vector3();
						box.getCenter(center);
						box.getSize(size);
						
						return {
							box: box.clone(),
							min: box.min.clone(),
							max: box.max.clone(),
							center: center.clone(),
							size: size.clone(),
							frame: targetFrame,
							isEmpty: false
						};
					} else {
						// 空场景的默认包围盒
						return {
							box: new THREE.Box3(),
							min: new THREE.Vector3(0, 0, 0),
							max: new THREE.Vector3(0, 0, 0),
							center: new THREE.Vector3(0, 0, 0),
							size: new THREE.Vector3(0, 0, 0),
							frame: targetFrame,
							isEmpty: true
						};
					}
				} finally {
					// 恢复原始状态
					this.state.playback.currentFrame = originalFrame;
					// 恢复可视化状态
					this.updateVisuals(originalFrame);
				}
			}

			getBBoxForCurrentFrame() {
				const currentFrame = Math.floor(this.state.playback.currentFrame);
				const animationBBoxData = this.state.animationBBoxData;
				
				// 如果系统未初始化，直接使用原始方法计算当前帧
				if (!animationBBoxData.isInitialized) {
					const box = this.getBBox();
					if (!box.isEmpty()) {
						const center = new THREE.Vector3();
						const size = new THREE.Vector3();
						box.getCenter(center);
						box.getSize(size);
						
						return {
							box: box.clone(),
							center: center.clone(),
							size: size.clone(),
							min: box.min.clone(),
							max: box.max.clone(),
							frame: currentFrame,
							isEmpty: false
						};
					} else {
						return {
							box: new THREE.Box3(),
							center: new THREE.Vector3(0, 0, 0),
							size: new THREE.Vector3(0, 0, 0),
							min: new THREE.Vector3(0, 0, 0),
							max: new THREE.Vector3(0, 0, 0),
							frame: currentFrame,
							isEmpty: true
						};
					}
				}
				
				// 1. 检查是否为采样帧
				if (animationBBoxData.sampledFrames.has(currentFrame)) {
					return animationBBoxData.sampledFrames.get(currentFrame);
				}
				
				// 2. 检查缓存
				if (animationBBoxData.cachedFrames.has(currentFrame)) {
					return animationBBoxData.cachedFrames.get(currentFrame);
				}
				
				// 3. 实时计算并缓存（LRU策略）
				const bboxData = this.getBBoxForFrame(currentFrame);
				
				// 缓存管理：限制缓存大小（例如最多10帧）
				const cachedFrames = animationBBoxData.cachedFrames;
				if (cachedFrames.size >= 10) {
					// 移除最旧的缓存（按帧号）
					const oldestFrame = Array.from(cachedFrames.keys()).sort((a, b) => a - b)[0];
					cachedFrames.delete(oldestFrame);
				}
				
				cachedFrames.set(currentFrame, bboxData);
				return bboxData;
			}

			getBBox() {
				const box = new THREE.Box3();
				box.makeEmpty();
				
				let includedObjects = [];
				let excludedObjects = [];
				
				const currentFrame = Math.floor(this.state.playback.currentFrame);
				
				// 遍历场景中所有物体
				this.scene.traverse((object) => {
					// 检查是否应该被排除
					const shouldExclude = this.shouldExcludeFromBBox(object);
					
					if (shouldExclude) {
						excludedObjects.push((object.name || object.type) + ' (' + object.constructor.name + ')');
						return;
					}
					
					if (object.visible) {
						// 特殊处理：SMPL 模型 - 计算当前帧的包围盒
						if (object === this.state.smplMesh && this.state.smplData) {
							try {
								// 计算当前帧的 SMPL 包围盒
								const smplBox = this.getSMPLBBox(currentFrame);
								
								if (smplBox && !smplBox.isEmpty()) {
									box.union(smplBox);
									includedObjects.push('SMPL_Mesh (current frame ' + currentFrame + ')');
								} else {
									excludedObjects.push('SMPL_Mesh (empty bbox for frame ' + currentFrame + ')');
								}
								return;
							} catch (error) {
								excludedObjects.push('SMPL_Mesh (error: ' + error.message + ')');
								return;
							}
						}
						
						// 普通物体
						try {
							const objectBox = new THREE.Box3();
							objectBox.setFromObject(object);
							
							// 检查包围盒是否有效
							if (!objectBox.isEmpty()) {
								box.union(objectBox);
								includedObjects.push((object.name || object.type) + ' (' + object.constructor.name + ')');
							} else {
								excludedObjects.push((object.name || object.type) + ' (' + object.constructor.name + ' - empty bbox)');
							}
						} catch (error) {
							excludedObjects.push((object.name || object.type) + ' (' + object.constructor.name + ' - error)');
						}
					} else {
						excludedObjects.push((object.name || object.type) + ' (' + object.constructor.name + ' - invisible)');
					}
				});
				return box;
			}

			getSMPLBBox(frame) {
				const smplMesh = this.state.smplMesh;
				const smplData = this.state.smplData;
				
				if (!smplMesh || !smplData || !smplData.vertices || !smplData.numVerts) {
					return new THREE.Box3(); // 返回空包围盒
				}
				
				// 确保帧号在有效范围内
				const numFrames = smplData.numFrames || 1;
				const f = Math.max(0, Math.min(Math.floor(frame), numFrames - 1));
				const numVerts = smplData.numVerts;
				
				// 从顶点数组中提取当前帧的顶点
				const vertices = smplData.vertices;
				const startIdx = f * numVerts * 3;
				
				// 创建包围盒
				const boundingBox = new THREE.Box3();
				
				// 遍历当前帧的所有顶点，扩展包围盒
				for (let i = 0; i < numVerts; i++) {
					const idx = startIdx + i * 3;
					const x = vertices[idx];
					const y = vertices[idx + 1];
					const z = vertices[idx + 2];
					
					boundingBox.expandByPoint(new THREE.Vector3(x, y, z));
				}
				
				// 应用 SMPL 网格的世界变换
				if (smplMesh.matrixWorld) {
					boundingBox.applyMatrix4(smplMesh.matrixWorld);
				}
				
				return boundingBox;
			}

			centerToObject() {
				// 1. 场景相机禁用
				if (this.state.cameras.currentType === 'scene' || (this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled)) {
					return;
				}
				
				// 2. 获取当前帧的包围盒数据
				const bboxData = this.getBBoxForCurrentFrame();
				
				// 3. 检查是否有物体
				if (bboxData.isEmpty) {
					// 空场景：维持相机和control target的相对距离，将control target挪至create pose的control target位置
					const camera = this.camera;
					const createPose = camera.userData.creationPose;
					
					if (createPose) {
						// 计算相对位移
						const delta = this.controls.target.clone().sub(camera.position);
						
						// 移动control target到创建位置
						const targetPos = createPose.controlsTarget || new THREE.Vector3(0, 1, 0);
						this.controls.target.copy(targetPos);
						
						// 相应移动相机位置
						camera.position.copy(this.controls.target.clone().sub(delta));
						
						// 恢复相机的clip plane为create pose值
						if (createPose.near !== undefined) {
							camera.near = createPose.near;
						}
						if (createPose.far !== undefined) {
							camera.far = createPose.far;
						}
						
						// 更新UI
						if (this.dom.inputs.near) {
							this.dom.inputs.near.value = camera.near.toFixed(2);
						}
						if (this.dom.inputs.far) {
							this.dom.inputs.far.value = camera.far.toFixed(2);
						}
						
						// 更新控制器和相机投影矩阵
						this.controls.update();
						camera.updateProjectionMatrix();
						
						// 保存状态并更新UI
						this.saveCurrentCameraState();
						this.updateCameraUIForMode();
					}
					
					return;
				}
				
				const center = bboxData.center.clone();
				const boxSize = bboxData.size.clone();
				
				// 4. 保存当前相机状态
				this.saveCurrentCameraState();
				
				// 5. 计算bounding box的最大维度
				const maxDimension = Math.max(boxSize.x, boxSize.y, boxSize.z);
				
				// 6. 维持相机与control target相对位移，移动control target到场景中心
				const delta = center.clone().sub(this.controls.target);
				
				this.controls.target.copy(center);
				this.camera.position.add(delta);
				
				// 7. 根据相机类型调整
				const container = this.dom.container;
				const aspect = container.clientWidth / container.clientHeight;
				
				if (this.camera.isOrthographicCamera) {
					// 正交相机调整
					this.adjustOrthoCamPosForBBox(center, boxSize, aspect, maxDimension);
				} else {
					// 透视相机调整
					this.adjustPerspCamPosForBBox(center, boxSize, aspect, maxDimension, false);
				}
				
				// 8. 更新控制器和相机
				this.controls.update();
				this.camera.updateProjectionMatrix();
				
				// 9. 保存新状态
				this.saveCurrentCameraState();
				
				// 10. 更新UI
				this.updateCameraUIForMode();
				this.onWindowResize();
			}

			adjustOrthoCamPosForBBox(center, boxSize, aspect, maxDimension) {
				const camera = this.camera;
				const margin = 1.05; // 5%边界
				
				// 如果是自定义相机的正交模式，要取三个维度最大值为边的立方体对角线长度
				if (!camera.userData.fixedView) {
					maxDimension = maxDimension * 1.72;
				}
				
				// 1. 保持相机和control target的相对位移，将control target挪至中心点（已完成）
				
				// 2. 根据bounding box的三个维度尺寸，取最大值，将相机位置挪至距离中心点（也就是control target）三个维度最大值为边的立方体对角线长度的位置
				const newDistance = maxDimension;
				
				// 计算当前相机到control target的方向
				const direction = new THREE.Vector3()
					.subVectors(camera.position, this.controls.target)
					.normalize();
				
				// 调整相机位置
				camera.position.copy(this.controls.target)
					.add(direction.multiplyScalar(newDistance));
				
				// 3. 根据当前相机的view width和view height，与bounding box的三个维度尺寸进行比对
				// 计算所需的viewHeight
				const requiredHeight = boxSize.y * margin;
				const requiredWidth = Math.max(boxSize.x, boxSize.z) * margin;
				
				// 根据宽高比计算需要的viewHeight
				const widthBasedHeight = requiredWidth / aspect;
				const viewHeight = Math.max(requiredHeight, widthBasedHeight);
				
				// 确保viewHeight至少为0.01
				const finalViewHeight = Math.max(viewHeight, 0.01);
				
				// 更新正交相机
				this.updateOrthographicFromViewHeight(camera, finalViewHeight);
				
				if (this.dom.inputs.fov) {
					this.dom.inputs.fov.value = finalViewHeight.toFixed(2);
				}
				
				// 更新相机userData
				camera.userData.viewHeight = finalViewHeight;
				const initialViewHeight = camera.userData.initialViewHeight;
				camera.userData.actualZoomFactor = initialViewHeight / finalViewHeight;
			}

			adjustPerspCamPosForBBox(center, boxSize, aspect, maxDimension, complex) {
				const camera = this.camera;
				const margin = 1.05; // 5%边界
					
				// 1. 保持相机和control target的相对位移，将control target挪至中心点（已完成）
				
				// 2. 根据所有物体的bounding box的三个维度尺寸，相机的fov和视窗aspect ratio，反推出要满画幅显示物体bounding box的相机与control target的距离
				
				// 计算相机FOV（弧度）
				const verticalFov = THREE.MathUtils.degToRad(camera.fov);
				const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * aspect);
				
				let halfWidth = 0;
				let halfHeight = 0;
				
				if (complex) {
					// 计算在观察方向上的投影尺寸
					// 获取相机当前观察方向
					const lookDirection = new THREE.Vector3()
						.subVectors(camera.position, this.controls.target)
						.normalize();
					
					// 计算物体在观察平面上的投影尺寸
					// 我们需要考虑物体在不同轴上的投影
					const viewMatrix = new THREE.Matrix4().lookAt(
						new THREE.Vector3(0, 0, 0),
						lookDirection,
						new THREE.Vector3(0, 1, 0)  // 假设世界坐标系Y向上
					);
					
					const objectToView = new THREE.Matrix3().setFromMatrix4(viewMatrix);
					
					// 物体各轴在世界坐标系中的方向
					const axes = [
						new THREE.Vector3(1, 0, 0),  // X轴
						new THREE.Vector3(0, 1, 0),  // Y轴
						new THREE.Vector3(0, 0, 1)   // Z轴
					];
					
					axes.forEach((axis, index) => {
						const size = boxSize.getComponent(index); // 获取对应轴的尺寸
						if (size > 0) {
							// 将轴转换到观察坐标系
							const axisInView = axis.applyMatrix3(objectToView);
							// 累加在各轴上的投影贡献
							halfWidth += Math.abs(size * axisInView.x);
							halfHeight += Math.abs(size * axisInView.y);
						}
					});
				} else {
					// 简化的投影尺寸计算
					// 假设相机大致正对物体，使用包围盒的最大尺寸
					// 高度：使用Y轴尺寸
					// 宽度：使用X和Z轴中较大的，并考虑宽高比
					halfHeight = boxSize.y / 2;
					halfWidth = Math.max(boxSize.x, boxSize.z) / 2;
				}
				
				// 计算距离
				const distanceHeight = (halfHeight * margin) / Math.tan(verticalFov / 2);
				const distanceWidth = (halfWidth * margin) / Math.tan(horizontalFov / 2);
				
				// 取较大值确保物体完全可见
				let distance = Math.max(distanceHeight, distanceWidth) * (complex ? 0.5 : 1.72 * (0.58 + (camera.fov / 180) * 0.42));
				
				// 添加安全距离（基于最大维度）
				const safeDistance = maxDimension * 0.5 * margin;
				distance = Math.max(distance, safeDistance);
				
				// 确保最小距离
				const finalDistance = Math.max(distance, 0.01);
				
				// 保持相机方向，调整位置
				const direction = new THREE.Vector3()
					.subVectors(camera.position, this.controls.target)
					.normalize();
				
				camera.position.copy(this.controls.target)
					.add(direction.multiplyScalar(finalDistance));
			}

			focusToObject() {
				// 1. 场景相机禁用
				if (this.state.cameras.currentType === 'scene' || (this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled)) {
					return;
				}
				
				// 2. 获取当前帧的包围盒数据
				const bboxData = this.getBBoxForCurrentFrame();
				
				// 3. 检查是否有物体
				if (bboxData.isEmpty) {
					return;
				}
				
				const center = bboxData.center.clone();
				const boxSize = bboxData.size.clone();
				
				// 4. 保存当前相机状态（以便只修改裁剪平面）
				this.saveCurrentCameraState();
				
				// 5. 计算bounding box的最大维度
				const maxDimension = Math.max(boxSize.x, boxSize.y, boxSize.z);
				
				// 6. 根据相机类型调整裁剪平面
				if (this.camera.isOrthographicCamera) {
					this.adjustOrthoCamClipForBBox(center, boxSize, maxDimension);
				} else {
					this.adjustPerspCamClipForBBox(center, boxSize, maxDimension);
				}
				
				// 7. 更新控制器和相机投影矩阵
				this.camera.updateProjectionMatrix();
				this.controls.update();
				
				// 8. 保存新状态（主要是裁剪平面）
				this.saveCurrentCameraState();
				
				// 9. 更新UI（特别是near/far输入框）
				this.updateCameraUIForMode();
			}

			adjustOrthoCamClipForBBox(center, boxSize, maxDimension) {
				const camera = this.camera;
				
				// 计算相机到目标的距离
				const distance = camera.position.distanceTo(center);
				
				// 对于默认正交相机的near clip和far clip
				const nearClip = Math.max(0.01, distance - maxDimension / 2);
				const farClip = maxDimension + nearClip;
				
				camera.near = nearClip;
				camera.far = farClip;
				
				// 更新UI
				if (this.dom.inputs.near) {
					this.dom.inputs.near.value = nearClip.toFixed(2);
				}
				if (this.dom.inputs.far) {
					this.dom.inputs.far.value = farClip.toFixed(2);
				}
			}

			adjustPerspCamClipForBBox(center, boxSize, maxDimension) {
				const camera = this.camera;
				
				// 计算相机到目标的距离
				const distance = camera.position.distanceTo(center);
				
				// 更新深度范围
				const nearClip = Math.max(0.01, distance - maxDimension * 1.72 / 2);
				const farClip = maxDimension * 1.72 + nearClip;
				
				camera.near = nearClip;
				camera.far = farClip;
				
				// 更新UI
				if (this.dom.inputs.near) {
					this.dom.inputs.near.value = nearClip.toFixed(2);
				}
				if (this.dom.inputs.far) {
					this.dom.inputs.far.value = farClip.toFixed(2);
				}
			}

			shouldExcludeFromBBox(object) {
				// 排除不可见物体
				if (!object.visible) return true;
				
				// 快速排除常见辅助对象
				if (object.isHelper) return true;
				
				// 检查构造函数名称
				const constructorName = object.constructor.name;
				if (constructorName.includes('Helper')) return true;
				
				// 排除相机
				if (object.isCamera) return true;
				
				// 排除灯光
				if (object.isLight) return true;
				
				// 特殊包含：SMPL帧网格
				if (object.userData && object.userData.isSMPLFrame) {
					return false;
				}
				
				// 排除Export容器组（ExportedScene和ImportedScene）
				if (object.name && (object.name === 'ExportedScene' || object.name === 'ImportedScene')) {
					return true;
				}
				
				// 特殊排除：网格辅助对象
				if (object.isMesh || object.isLine || object.isPoints) {
					// 检查用户数据标记
					if (object.userData && object.userData.isVisualization) return true;
					if (object.userData && object.userData.isCameraVisualization) return true;
					if (object.userData && object.userData.isLightVisualization) return true;
					
					// 检查名称模式
					const name = object.name.toLowerCase();
					const helperKeywords = [
						'helper', 'grid', 'axis', 'axes', 'arrow', 'sphere', 
						'visualization', 'boxhelper', 'camera', 'light',
						'辅助', '网格', '坐标', '箭头', '球体', '可视化'
					];
					
					for (const keyword of helperKeywords) {
						if (name.includes(keyword)) return true;
					}
					
					// 检查材质是否为辅助材质
					if (object.material) {
						// 如果是线框材质，可能是辅助对象
						if (object.material.wireframe === true) return true;
						
						// 检查材质名称
						if (object.material.name) {
							const matName = object.material.name.toLowerCase();
							if (matName.includes('helper') || matName.includes('grid')) return true;
						}
					}
				}
				
				// 排除其他类型的辅助对象
				if (object.isLine || object.isPoints) {
					const name = object.name.toLowerCase();
					if (name.includes('helper') || name.includes('grid') || name.includes('axis')) {
						return true;
					}
				}
				
				// 排除场景根节点
				if (object === this.scene) return true;
				
				// 排除Three.js内置辅助对象类型
				if (object.type === 'GridHelper' || object.type === 'AxesHelper') return true;
				
				// 检查父对象是否应该被排除
				if (object.parent && object.parent !== this.scene) {
					// 如果父对象是容器组，不要排除当前对象
					if (object.parent.name && (object.parent.name === 'ExportedScene' || object.parent.name === 'ImportedScene')) {
						return false;
					}
					
					// 检查父对象是否是辅助对象
					const parentName = object.parent.name ? object.parent.name.toLowerCase() : '';
					const parentConstructorName = object.parent.constructor.name;
					const parentType = object.parent.type;
					
					// 如果父对象是ArrowHelper、GridHelper、AxesHelper等，排除当前对象
					if (object.parent.isHelper || 
						parentConstructorName.includes('Helper') || 
						parentType === 'ArrowHelper' || 
						parentType === 'GridHelper' || 
						parentType === 'AxesHelper' ||
						parentName.includes('helper') ||
						parentName.includes('arrow') ||
						parentName.includes('grid') ||
						parentName.includes('axis')) {
						return true;
					}
					
					// 进一步检查父对象的父对象（递归）
					if (this.shouldExcludeFromBBox(object.parent)) {
						return true;
					}
				}
				
				return false;
			}

			// 相机管理
			createDefaultCameras() {
				this.state.cameras.default = [];
				const aspect = window.innerWidth / window.innerHeight;
				const orthoSize = 5;
				
				// 定义固定视图相机名称数组
				const FIXED_VIEW_CAMERAS = ["Front", "Back", "Left", "Right", "Top", "Bottom"];
				
				const createCam = (name, type, pos, lookAt) => {
					let cam;
					if (type === 'Perspective') {
						cam = new THREE.PerspectiveCamera(50, aspect, 0.01, 500);
						cam.userData.isDefault = true;
						cam.userData.orthographic = false;
						cam.userData.initialDistance = new THREE.Vector3(...pos).distanceTo(new THREE.Vector3(...lookAt));
					} else {
						cam = new THREE.OrthographicCamera(-orthoSize * aspect, orthoSize * aspect, orthoSize, -orthoSize, 0.01, 500);
						cam.userData.isDefault = true;
						cam.userData.orthographic = true;
						cam.userData.viewHeight = orthoSize * 2;
						cam.userData.initialViewHeight = orthoSize * 2;
					}
					
					cam.position.set(...pos);
					cam.lookAt(...lookAt);
					cam.name = name;
					
					cam.userData.fixedView = FIXED_VIEW_CAMERAS.includes(name);
					cam.userData.controlsTarget = new THREE.Vector3(...lookAt);
					cam.userData.upVector = new THREE.Vector3(0, 1, 0);
					
					cam.userData.creationPose = {
						position: cam.position.clone(),
						rotation: cam.rotation.clone(),
						fov: cam.fov,
						near: cam.near,
						far: cam.far,
						orthographic: cam.isOrthographicCamera,
						viewHeight: cam.userData.viewHeight,
						initialViewHeight: cam.userData.initialViewHeight,
						initialDistance: cam.userData.initialDistance,
						actualZoomFactor: 1.0,
						controlsTarget: cam.userData.controlsTarget,
						rollAngle: 0,
						upVector: new THREE.Vector3(0, 1, 0),
						fixedView: cam.userData.fixedView
					};
					
					return cam;
				};
				
				this.state.cameras.default.push(createCam("User", 'Perspective', [0, 1, 4], [0, 1, 0]));
				this.state.cameras.default.push(createCam("Front", 'Ortho', [0, 0, 50], [0, 0, 0]));
				this.state.cameras.default.push(createCam("Back", 'Ortho', [0, 0, -50], [0, 0, 0]));
				this.state.cameras.default.push(createCam("Left", 'Ortho', [50, 0, 0], [0, 0, 0]));
				this.state.cameras.default.push(createCam("Right", 'Ortho', [-50, 0, 0], [0, 0, 0]));
				this.state.cameras.default.push(createCam("Top", 'Ortho', [0, 50, 0], [0, 0, 0]));
				this.state.cameras.default.push(createCam("Bottom", 'Ortho', [0, -50, 0], [0, 0, 0]));
			}

			createCustomCamera() {
				if (this.state.cameras.customCount >= 30) { 
					this.showMessage("Cannot create more than 30 custom cameras", 5000); 
					return; 
				}
				
				if (this.state.playback.isPlaying) this.pause();
				
				const name = "CustomCamJK_" + (this.state.cameras.customCount + 1).toString().padStart(2, '0');
				
				// 根据当前相机的投影类型创建新相机
				let newCam;
				const container = this.dom.container;
				const aspect = container.clientWidth / container.clientHeight;
				
				// 确定当前相机的实际状态
				let currentCameraState = this.getCurrentCameraState(this.camera);
				
				if (currentCameraState.isOrthographic) {
					// 创建正交相机
					const viewHeight = currentCameraState.viewHeight || 5;
					newCam = new THREE.OrthographicCamera(
						-viewHeight * aspect / 2,
						viewHeight * aspect / 2,
						viewHeight / 2,
						-viewHeight / 2,
						currentCameraState.near,
						currentCameraState.far
					);
					newCam.userData.viewHeight = viewHeight;
					newCam.userData.initialViewHeight = viewHeight;
					newCam.userData.actualZoomFactor = 1.0;
				} else {
					// 创建透视相机
					newCam = new THREE.PerspectiveCamera(
						currentCameraState.fov,
						aspect,
						currentCameraState.near,
						currentCameraState.far
					);
				}
				
				newCam.name = name;
				
				const rollResult = this.calculateCameraRollAngle(this.camera);
				const currentRollAngle = rollResult.roll;
				const upVector = rollResult.upVector || this.camera.userData.upVector.clone() || this.camera.up.clone();
				
				// 应用从当前相机获取的当前帧状态
				newCam.position.copy(currentCameraState.position);
				newCam.up.copy(upVector);
				newCam.rotation.copy(currentCameraState.rotation);
				
				if (currentCameraState.isOrthographic) {
					// 对于正交相机，确保viewHeight正确设置
					if (!newCam.userData.viewHeight) {
						newCam.userData.viewHeight = currentCameraState.viewHeight;
					}
				}
				
				// 设置用户数据
				newCam.userData = {
					controlsTarget: currentCameraState.controlsTarget.clone(),
					viewHeight: currentCameraState.viewHeight,
					initialViewHeight: currentCameraState.isOrthographic ? currentCameraState.viewHeight : null,
					actualZoomFactor: 1.0,
					keyframes: [],
					rollAngle: currentRollAngle,
					upVector: upVector,
					near: currentCameraState.near,
					far: currentCameraState.far,
					creationPose: {
						position: newCam.position.clone(),
						rotation: newCam.rotation.clone(),
						fov: newCam.fov,
						near: newCam.near,
						far: newCam.far,
						orthographic: currentCameraState.isOrthographic,
						viewHeight: currentCameraState.viewHeight,
						initialViewHeight: currentCameraState.isOrthographic ? currentCameraState.viewHeight : null,
						initialDistance: currentCameraState.initialDistance || currentCameraState.position.distanceTo(this.controls.target),
						actualZoomFactor: 1.0,
						controlsTarget: currentCameraState.controlsTarget.clone(),
						rollAngle: currentRollAngle,
						upVector: upVector
					}
				};
				
				// 保存相机状态到全局缓存
				this.state.cameras.states.set(name, {
					position: newCam.position.clone(),
					rotation: newCam.rotation.clone(),
					fov: newCam.fov,
					near: newCam.near,
					far: newCam.far,
					zoom: newCam.zoom || 1,
					controlsTarget: currentCameraState.controlsTarget.clone(),
					orthographic: currentCameraState.isOrthographic,
					viewHeight: currentCameraState.viewHeight,
					rollAngle: currentRollAngle,
					up: upVector
				});
				
				/* if (currentRollAngle !== 0 && this.state.cameras.currentType !== 'scene') {
					this.applyRollAngleToCamera(newCam, currentRollAngle, true);
					this.controls.update();
				} */
				
				this.scene.add(newCam);
				this.state.cameras.custom.push(newCam);
				this.state.cameras.customCount++;
				this.createCameraVisualization(newCam, 0xffaa00);
				this.updateViewsMenu();
				this.dom.inputs.views.value = name;
				this.switchToCamera(newCam, true);
			}

			deleteCurrentCustomCamera() {
				if (this.state.cameras.currentType !== 'custom') {
					return;
				}
				
				const cameraToDelete = this.camera;
				const cameraName = cameraToDelete.name;
				
				this.clearCameraAnimationData(cameraToDelete);
				
				this.scene.remove(cameraToDelete);
				if (cameraToDelete.userData.visualization) {
					cameraToDelete.userData.visualization.forEach(a => this.scene.remove(a));
				}
				
				const index = this.state.cameras.custom.findIndex(c => c.name === cameraName);
				if (index > -1) {
					this.state.cameras.custom.splice(index, 1);
				}
				
				this.state.cameras.states.delete(cameraName);
				this.state.cameras.customCount = Math.max(0, this.state.cameras.customCount - 1);
				
				// 如果相机动画启用，关闭它
				if (this.state.cameraAnim.isEnabled) {
					this.toggleCameraAnimation();
				}
				
				 // 清除动画关键帧
				this.state.cameraAnim.keyframes = [];
				this.state.cameras.activeScene = null;
				
				if (this.state.cameras.default.length > 0) {
					const userCamera = this.state.cameras.default[0];
					this.dom.inputs.views.value = "User";
					this.switchToCamera(userCamera);
				}
				
				this.updateViewsMenu();
				this.updateKeyframeCount();
				this.updateKeyframeButtonsState();
				this.updateCameraUIForMode();
				this.updateCameraControlsState();
			}

			switchToCamera(targetCamera, forceInitial = false) {
				this.saveCurrentCameraState();
				
				// 保存当前相机动画轨
				if (this.camera && this.state.cameras.currentType === 'custom' && this.camera.userData.keyframes !== undefined) {
					this.camera.userData.keyframes = [...this.state.cameraAnim.keyframes];
				}
				
				// 确定相机类型
				if (targetCamera.userData && targetCamera.userData.isDefault) {
					this.state.cameras.currentType = 'default';
					this.state.cameras.activeScene = null;
				} else if (targetCamera.name && targetCamera.name.startsWith('CustomCamJK_')) {
					this.state.cameras.currentType = 'custom';
					this.state.cameras.activeScene = null;
				} else {
					this.state.cameras.currentType = 'scene';
					this.state.cameras.activeScene = targetCamera;
				}
				
				const savedState = this.state.cameras.states.get(targetCamera.name);
				
				// 针对已经有saveState的默认相机以及非初创的自定义相机
				// 初创的自定义相机在创建阶段已经有saveState，而且姿态已是正确的
				// 场景相机始终读取当前帧姿态
				const isCustomWithAnimation = this.state.cameras.currentType === 'custom' && 
								   this.state.cameraAnim.isEnabled;
				const isSceneCamera = this.state.cameras.currentType === 'scene';
				
				if (!isSceneCamera && savedState && !forceInitial && !isCustomWithAnimation) {
					// 应用保存的状态
					targetCamera.position.copy(savedState.position);
					targetCamera.rotation.copy(savedState.rotation);
					targetCamera.fov = savedState.fov;
					targetCamera.near = savedState.near;
					targetCamera.far = savedState.far;
					
					if (!savedState.rollAngle || !savedState.up) {
						targetCamera.up.set(0, 1, 0);
					} else {
						targetCamera.up.copy(savedState.up);
					}
					
					if (targetCamera.isOrthographicCamera && savedState.viewHeight) {
						this.updateOrthographicFromViewHeight(targetCamera, savedState.viewHeight);
						targetCamera.userData.viewHeight = savedState.viewHeight;
					} else if (targetCamera.isPerspectiveCamera && savedState.zoom) {
						targetCamera.zoom = savedState.zoom;
					}
					
					targetCamera.updateProjectionMatrix();
					this.controls.target.copy(savedState.controlsTarget);
					
					if (savedState.rollAngle !== undefined) {
						targetCamera.userData.rollAngle = savedState.rollAngle;
					}
				} else {
					
					const currentFrame = Math.floor(this.state.playback.currentFrame);
					
					switch (this.state.cameras.currentType) {
						case 'scene':
							// 场景相机：立即应用当前帧的姿态到所有场景相机
							this.updateAllSceneCameraPose(currentFrame);
							break;
							
						case 'custom':
							if (forceInitial) {
								// 不处理初创自定义相机
								if (!targetCamera.userData.rollAngle || !targetCamera.userData.upVector) {
									targetCamera.up.set(0, 1, 0);
								} else {
									targetCamera.up.copy(targetCamera.userData.upVector);
								}
							} else if (isCustomWithAnimation) {
								// 自定义相机且启用了动画：立即应用当前帧的姿态
								this.updateCurrentCustomCameraPose(currentFrame);
								this.updateUIValuesFromCustomCamera();
							} else {
								// 未启用动画的没有savestate的自定义相机
								// 逻辑上存在，实际不存在
								const target = this.getCameraSavedState(targetCamera);
								this.controls.target.copy(target);
							}
							break;
							
						case 'default':
						default:
							// 默认相机：使用公共函数设置初始目标点
							const target = this.getCameraSavedState(targetCamera);
							this.controls.target.copy(target);
							if (!targetCamera.userData.rollAngle || !targetCamera.userData.upVector) {
								targetCamera.up.set(0, 1, 0);
							} else {
								targetCamera.up.copy(targetCamera.userData.upVector);
							}
							break;
					}
				}
				
				this.camera = targetCamera;
				this.controls.object = this.camera;
				
				// 加载目标相机的专属动画轨
				if (targetCamera.userData.keyframes !== undefined) {
					if (this.state.cameras.currentType === 'custom') {
						this.state.cameraAnim.keyframes = [...targetCamera.userData.keyframes];
					} else if (this.state.cameras.currentType === 'scene') {
						this.state.cameraAnim.keyframes = [...targetCamera.userData.keyframes];
					} else {
						this.state.cameraAnim.keyframes = [];
					}
				} else {
					this.state.cameraAnim.keyframes = [];
				}
				
				// 同步 roll 输入框
				if (this.dom.inputs.rollAngle) {
					if (targetCamera.userData.rollAngle !== undefined) {
						this.dom.inputs.rollAngle.value = targetCamera.userData.rollAngle.toFixed(2);
					} else {
						this.dom.inputs.rollAngle.value = "0.00";
						targetCamera.userData.rollAngle = 0;
					}
				}
				
				if (this.dom.inputs.near && this.dom.inputs.far) {
					this.dom.inputs.near.value = this.camera.near.toFixed(2);
					this.dom.inputs.far.value = this.camera.far.toFixed(2);
				}
				
				// 设置控制限制
				const isFixedView = targetCamera.userData.isDefault && targetCamera.userData.fixedView;
				
				// 如果是场景相机，禁用所有控制
				if (this.state.cameras.currentType === 'scene') {
					this.controls.enabled = false;
				} else if (this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled) {
					// 自定义相机且启用了动画：禁用所有控制
					this.controls.enabled = false;
				} else {
					// 默认相机和未启用动画的自定义相机
					this.controls.enabled = true;
					this.controls.enableRotate = !isFixedView;
				}
				
				// 更新其他UI
				this.updateOrthoToggleState();
				this.updateCameraUIForMode();
				this.updateKeyframeButtonsState();
				this.updateAutoAddKeyframeButtonState();
				this.updateVisualizationVisibility();
				this.updateKeyframeCount();
				this.updatePostProcessing();
				this.onWindowResize();
				
				// 更新select元素的颜色
				if (this.dom.inputs.views) {
					this.dom.inputs.views.value = targetCamera.name;
					this.updateSelectColor();
				}
				
				// 不能启用更新控制
				// 会导致导出时无关键帧场景自由相机朝向默认控制目标(0, 1, 0)
				// 会导致开启动画的自定义相机在关闭动画后操作异常
				if (!isSceneCamera && !isCustomWithAnimation) {
					this.controls.update();
				}
			}

			resetCamera() {
				// 对场景相机禁用
				if (this.state.cameras.currentType === 'scene') {
					return;
				}
				
				const type = this.state.cameras.currentType;
				const camera = this.camera;
				
				const creationPose = camera.userData.creationPose;
				if (creationPose) {
					const hasKeyframes = camera.userData.keyframes && camera.userData.keyframes.length > 0;
					
					// 保存当前投影类型（对于有关键帧的相机，保持当前类型）
					let targetIsOrthographic = creationPose.orthographic;
					if (type === 'custom' && hasKeyframes) {
						// 有关键帧的自定义相机：保持当前投影类型
						targetIsOrthographic = camera.isOrthographicCamera;
					}
					
					// 投影类型不一致时重建相机
					if (camera.isOrthographicCamera !== targetIsOrthographic) {
						const container = this.dom.container;
						const aspect = container.clientWidth / container.clientHeight;
						
						let newCamera;
						let viewHeight;
						let fov;
						
						// 计算创建时相机到目标点的距离
						let creationDistance = 4;
						if (creationPose.initialDistance) {
							creationDistance = creationPose.initialDistance;
						} else if (creationPose.controlsTarget) {
							// 如果没有保存initialDistance，根据位置和controlsTarget计算
							creationDistance = creationPose.position.distanceTo(creationPose.controlsTarget);
						}
						
						if (targetIsOrthographic) {
							// 重建正交相机
							if (creationPose.orthographic) {
								// 创建时就是正交：使用创建时的viewHeight
								viewHeight = creationPose.initialViewHeight || creationPose.viewHeight || 10;
							} else {
								// 创建时是透视：根据创建时的fov和距离计算viewHeight
								viewHeight = this.calculateViewHeightFromFov(creationPose.fov, creationDistance);
							}
							
							newCamera = new THREE.OrthographicCamera(
								-viewHeight * aspect / 2,
								viewHeight * aspect / 2,
								viewHeight / 2,
								-viewHeight / 2,
								creationPose.near,
								creationPose.far
							);
							
							newCamera.userData.viewHeight = viewHeight;
							newCamera.userData.initialViewHeight = viewHeight;
							newCamera.userData.actualZoomFactor = 1.0;
						} else {
							// 重建透视相机
							if (creationPose.orthographic) {
								// 创建时是正交：根据创建时的viewHeight和距离计算fov
								const creationViewHeight = creationPose.initialViewHeight || creationPose.viewHeight || 10;
								fov = this.calculateFovFromViewHeight(creationViewHeight, creationDistance);
							} else {
								// 创建时就是透视：使用创建时的fov
								fov = creationPose.fov;
							}
							
							newCamera = new THREE.PerspectiveCamera(
								fov,
								aspect,
								creationPose.near,
								creationPose.far
							);
						}
						
						newCamera.name = camera.name;
						newCamera.position.copy(creationPose.position);
						newCamera.up.copy(creationPose.upVector);
						newCamera.rotation.copy(creationPose.rotation);
						
						newCamera.userData = {
							isDefault: camera.userData.isDefault,
							creationPose: {
								...creationPose,
								initialDistance: creationDistance
							},
							actualZoomFactor: 1.0,
							rollAngle: creationPose.rollAngle || 0,
							fixedView: camera.userData.fixedView,
							near: newCamera.near,
							far: newCamera.far 
						};
						
						// 复制关键帧（如果有）
						if (camera.userData.keyframes) {
							newCamera.userData.keyframes = [...camera.userData.keyframes];
						}
						
						// 立即替换相机并同步UI
						this.camera = newCamera;
						this.controls.object = newCamera;
						
						const replaceInArray = (array) => {
							const idx = array.findIndex(c => c.name === camera.name);
							if (idx >= 0) array[idx] = newCamera;
						};
						
						if (type === 'default') {
							replaceInArray(this.state.cameras.default);
						} else if (type === 'custom') {
							replaceInArray(this.state.cameras.custom);
						}
						
						/* if (creationPose.rollAngle) {
							this.applyRollAngleToCamera(newCamera, creationPose.rollAngle, true);
						} */
						
						// 立即同步UI状态和投影类型
						this.dom.toggles.ortho.checked = newCamera.isOrthographicCamera;
					} else {
						// 投影类型一致时直接恢复属性
						camera.position.copy(creationPose.position);
						camera.up.copy(creationPose.upVector);
						camera.rotation.copy(creationPose.rotation);
						camera.near = creationPose.near;
						camera.far = creationPose.far;
						
						// 计算当前相机到创建时的控制目标点的距离
						let creationDistance = 4;
						if (creationPose.initialDistance) {
							creationDistance = creationPose.initialDistance;
						} else if (creationPose.controlsTarget) {
							// 使用创建时的位置和控制目标点计算
							creationDistance = creationPose.position.distanceTo(creationPose.controlsTarget);
						}
						
						// 根据当前投影类型设置fov/viewHeight
						if (camera.isOrthographicCamera) {
							if (creationPose.orthographic) {
								// 创建时是正交：使用创建时的viewHeight
								const initialViewHeight = creationPose.initialViewHeight || creationPose.viewHeight || 10;
								this.updateOrthographicFromViewHeight(camera, initialViewHeight);
								camera.userData.viewHeight = initialViewHeight;
							} else {
								// 创建时是透视：根据创建时的fov和当前距离计算viewHeight
								const viewHeight = this.calculateViewHeightFromFov(creationPose.fov, creationDistance);
								this.updateOrthographicFromViewHeight(camera, viewHeight);
								camera.userData.viewHeight = viewHeight;
							}
							camera.userData.actualZoomFactor = 1.0;
						} else {
							if (creationPose.orthographic) {
								// 创建时是正交：根据创建时的viewHeight和当前距离计算fov
								const creationViewHeight = creationPose.initialViewHeight || creationPose.viewHeight || 10;
								camera.fov = this.calculateFovFromViewHeight(creationViewHeight, creationDistance);
							} else {
								// 创建时就是透视：使用创建时的fov
								camera.fov = creationPose.fov;
							}
						}
						
						/* if (creationPose.rollAngle) {
							this.applyRollAngleToCamera(camera, creationPose.rollAngle, true);
						} */
					}
					
					// 更新相机userData
					camera.userData.rollAngle = creationPose.rollAngle || 0;
					camera.userData.upVector = creationPose.upVector.clone();
					camera.userData.near = camera.near;
					camera.userData.far = camera.far;
					
					// 更新相机状态缓存中的up向量和rollAngle
					const savedState = this.state.cameras.states.get(camera.name);
					if (savedState) {
						savedState.up = creationPose.upVector.clone();
						savedState.rollAngle = creationPose.rollAngle || 0;
						// 确保缓存中的其他状态也正确
						savedState.position = camera.position.clone();
						savedState.rotation = camera.rotation.clone();
						savedState.fov = camera.fov;
						savedState.near = camera.near;
						savedState.far = camera.far;
						savedState.orthographic = camera.isOrthographicCamera;
						savedState.viewHeight = camera.userData.viewHeight;
						
						this.state.cameras.states.set(camera.name, savedState);
					}
					
					if (this.dom.inputs.rollAngle) {
						this.dom.inputs.rollAngle.value = (creationPose.rollAngle || 0).toFixed(2);
					}
					
					this.dom.inputs.near.value = this.camera.near.toFixed(2);
					this.dom.inputs.far.value = this.camera.far.toFixed(2);
					
					// 根据相机类型设置正确的旋转中心
					let targetPosition;
					if (camera.userData.isDefault) {
						if (camera.name === 'User') {
							targetPosition = new THREE.Vector3(0, 1, 0);
						} else {
							targetPosition = new THREE.Vector3(0, 0, 0);
						}
					} else {
						targetPosition = creationPose.controlsTarget || new THREE.Vector3(0, 1, 0);
					}
					
					this.controls.target.copy(targetPosition);
					this.controls.update();
					camera.updateProjectionMatrix();
				}
				
				this.updateCameraUIForMode();
				this.onWindowResize();
				
				this.saveCurrentCameraState();
			}

			// 相机界面
			toggleCameraAnimation() {
				// 仅自定义相机可以切换
				if (this.state.cameras.currentType !== 'custom') {
					return;
				}
				
				// 混合投影类型关键帧的检查
				if (!this.state.cameraAnim.isEnabled && this.state.cameraAnim.keyframes.length > 0) {
					// 检查关键帧中的投影类型
					const keyframes = this.state.cameraAnim.keyframes;
					let hasOrthographic = false;
					let hasPerspective = false;
					
					keyframes.forEach(kf => {
						if (kf.isOrthographic) {
							hasOrthographic = true;
						} else {
							hasPerspective = true;
						}
					});
					
					// 如果混合类型，显示警告
					if (hasOrthographic && hasPerspective) {
						/* this.showMessage("Warning: Keyframes contain mixed projection types; the state of the first frame is used.", 3000); */
					}
				}
				
				this.state.cameraAnim.isEnabled = !this.state.cameraAnim.isEnabled;
				
				if (this.state.playback.isPlaying && !this.state.cameraAnim.isEnabled) this.pause();
				
				// 设置控制器状态
				if (this.state.cameraAnim.isEnabled) {
					// 进入 play mode
					this.state.cameraAnim.originalControlsEnabled = this.controls.enabled;
					this.controls.enabled = false;
				} else {
					// 进入 edit mode
					this.controls.enabled = this.state.cameraAnim.originalControlsEnabled;
					
					// 纠正插值计算control target位置误差
					// 减少从play mode切换到edit mode时的相机姿态变化
					// 注意：如果在updateCurrentCustomCameraPose中强制运行applyRollAngleToCamera
					// 虽然可以完美匹配动画姿态与orbit control姿态，但是实际操作并不好
					const correctedTarget = this.ControlTargetPosCorrection();
					
					// 同步控制器状态，默认不处理，可用this.state.playback.startFrame调试
					this.syncControlsFromCamera(0, correctedTarget);
					
					const rollResult = this.calculateCameraRollAngle(this.camera);
					this.camera.up = rollResult.upVector;
				}
				
				this.updateKeyframeButtonsState();
				this.updateOrthoToggleState();
				this.updateCameraControlsState();
				this.onWindowResize();
			}

			ControlTargetPosCorrection() {
				if (!this.camera) return;
				
				const currentFrame = Math.floor(this.state.playback.currentFrame);
				
				// 获取当前帧的插值结果
				const interpolated = this.getCameraPose(
					this.state.cameraAnim.keyframes,
					currentFrame,
					{
						includeControlsTarget: true,
						includeRoll: false,
						includeFov: false
					}
				);
				
				let originalDirection;
				let correctedTarget;
				let targetDistance = this.state.controlTargetDist.defDist;
				let originalDistance = this.state.controlTargetDist.defDist;
				let direction = new THREE.Vector3();
				
				if (!interpolated) {
					// 使用相机当前方向
					direction.set(0, 0, -1);
					direction.applyQuaternion(this.camera.quaternion);
					direction.normalize();
					
					// 从当前controls.target获取原始数据
					const currentControlsTarget = this.controls.target.clone();
					originalDistance = this.camera.position.distanceTo(currentControlsTarget);
					
					// 计算原始方向
					originalDirection = new THREE.Vector3().subVectors(
						currentControlsTarget, 
						this.camera.position
					).normalize();
					
					targetDistance = Math.max(
						this.state.controlTargetDist.minDist, 
						Math.min(this.state.controlTargetDist.maxDist, originalDistance)
					);
					
					correctedTarget = this.camera.position.clone().add(
						direction.clone().multiplyScalar(targetDistance)
					);
					
				} else {
					// 计算相机当前方向
					direction.set(0, 0, -1);
					direction.applyQuaternion(this.camera.quaternion);
					direction.normalize();
					
					// 计算距离
					if (interpolated.controlsTarget) {
						originalDistance = interpolated.position.distanceTo(interpolated.controlsTarget);
						originalDirection = new THREE.Vector3().subVectors(
							interpolated.controlsTarget, 
							interpolated.position
						).normalize();
					} else {
						// 尝试从关键帧获取
						const currentKeyframe = this.state.cameraAnim.keyframes.find(k => k.frame === currentFrame);
						if (currentKeyframe && currentKeyframe.controlsTarget) {
							originalDistance = this.camera.position.distanceTo(currentKeyframe.controlsTarget);
							originalDirection = new THREE.Vector3().subVectors(
								currentKeyframe.controlsTarget, 
								this.camera.position
							).normalize();
						}
					}
					
					targetDistance = Math.max(
						this.state.controlTargetDist.minDist, 
						Math.min(this.state.controlTargetDist.maxDist, originalDistance)
					);
					
					correctedTarget = this.camera.position.clone().add(
						direction.clone().multiplyScalar(targetDistance)
					);
				}
				/* 
				// === 统一日志输出 ===
				console.group("Control Target Correction - Frame " + currentFrame);
				
				// 1. 位置分析
				console.log("--- Position Analysis ---");
				const cameraPos = this.camera.position.clone();
				console.log("Camera Position: (" + 
					cameraPos.x.toFixed(2) + ", " + 
					cameraPos.y.toFixed(2) + ", " + 
					cameraPos.z.toFixed(2) + ")");
				
				// 显示原始目标
				if (!interpolated) {
					const currentControlsTarget = this.controls.target.clone();
					console.log("Original Target: (" + 
						currentControlsTarget.x.toFixed(2) + ", " + 
						currentControlsTarget.y.toFixed(2) + ", " + 
						currentControlsTarget.z.toFixed(2) + ")");
				} else if (interpolated.controlsTarget) {
					console.log("Original Target: (" + 
						interpolated.controlsTarget.x.toFixed(2) + ", " + 
						interpolated.controlsTarget.y.toFixed(2) + ", " + 
						interpolated.controlsTarget.z.toFixed(2) + ")");
				} else {
					const currentKeyframe = this.state.cameraAnim.keyframes.find(k => k.frame === currentFrame);
					if (currentKeyframe && currentKeyframe.controlsTarget) {
						console.log("Original Target (from keyframe): (" + 
							currentKeyframe.controlsTarget.x.toFixed(2) + ", " + 
							currentKeyframe.controlsTarget.y.toFixed(2) + ", " + 
							currentKeyframe.controlsTarget.z.toFixed(2) + ")");
					} else {
						console.log("Original Target: Not available");
					}
				}
				
				console.log("Corrected Target: (" + 
					correctedTarget.x.toFixed(2) + ", " + 
					correctedTarget.y.toFixed(2) + ", " + 
					correctedTarget.z.toFixed(2) + ")");
				
				// 2. 距离分析
				console.log("--- Distance Analysis ---");
				console.log("Original Distance: " + originalDistance.toFixed(2) + " units");
				console.log("Corrected Distance: " + targetDistance.toFixed(2) + " units");
				
				// 只有在原始距离有效时才计算变化百分比
				if (originalDistance > 0.001) {
					console.log("Distance Change: " + 
						(targetDistance - originalDistance).toFixed(2) + " units (" + 
						((targetDistance - originalDistance) / originalDistance * 100).toFixed(1) + "%)");
				}
				
				if (originalDistance < 0.5) {
					console.log("--- Validation ---");
					console.log("Note: Original distance very small (< 0.5)");
				} else if (originalDistance > 500) {
					console.log("--- Validation ---");
					console.log("Note: Original distance very large (> 500)");
				}
				
				// 3. 方向分析（如果有原始数据）
				console.log("--- Direction Analysis ---");
				const angleDifference = direction.angleTo(originalDirection) * (180 / Math.PI);
				console.log("Original Direction: (" + 
					originalDirection.x.toFixed(3) + ", " + 
					originalDirection.y.toFixed(3) + ", " + 
					originalDirection.z.toFixed(3) + ")");
				console.log("Corrected Direction: (" + 
					direction.x.toFixed(3) + ", " + 
					direction.y.toFixed(3) + ", " + 
					direction.z.toFixed(3) + ")");
				console.log("Direction Difference: " + angleDifference.toFixed(2) + " deg");
				
				// 方向差异分类
				if (angleDifference > 10) {
					console.log("Note: Significant direction correction: " + angleDifference.toFixed(1) + " deg");
				} else if (angleDifference > 1) {
					console.log("Note: Minor direction correction: " + angleDifference.toFixed(1) + " deg");
				} else {
					console.log("Note: Minimal direction correction: " + angleDifference.toFixed(1) + " deg");
				}
				
				// 4. 状态信息
				console.log("--- Status ---");
				console.log("Interpolation data: " + (interpolated ? "Available" : "Not available"));
				
				// 结束日志组
				console.groupEnd();
				 */
				// 更新控制器的target
				if (correctedTarget) {
					this.controls.target.copy(correctedTarget);
					this.camera.userData.controlsTarget = correctedTarget.clone();
					return correctedTarget;
				}
				
				return null;
			}

			recalculateControlsTargetFromCamera() {
				if (!this.camera) return;
				
				// 根据相机当前方向计算前方点
				const direction = new THREE.Vector3(0, 0, -1);
				direction.applyQuaternion(this.camera.quaternion);
				const lookAtPoint = this.camera.position.clone().add(direction.multiplyScalar(this.state.controlTargetDist.defDist));
				this.controls.target.copy(lookAtPoint);
				
				// 保存到相机userData以便后续使用
				this.camera.userData.controlsTarget = lookAtPoint.clone();
			}

			syncControlsFromCamera(t, correctedTarget) {
				if (!this.controls || !this.camera) return;
				
				switch (t) {
					
					// 很重要：不能更新或重置orbit control
					// 否则即便随着相机姿态更新了control target
					// 但spherical值不能同步更新
					// 从play mode切换edit mode后时
					// 如果当前没有关键帧，相机姿态会变
					case 0:	// 不处理：切换时姿态不变但control后跳动
					default:
						break;
					
					case 1:	// 更新（清零 delta 值）：切换时姿态跳动
						this.controls.update();
						break;
					
					case 2:	// 重置（计算 spherical 值）：切换时姿态跳动
						// 保存初始状态
						this.controls.saveState();
						this.controls.reset();
						break;
					
					case 3:	// 手动计算并设置 spherical 值：非公共接口不起作用（相当于case 0）
						try {
							if (this.controls.spherical) {
								const direction = new THREE.Vector3().subVectors(
									this.camera.position, 
									this.controls.target
								);
								this.controls.spherical.setFromVector3(direction);
								
								// 重置旋转增量
								if (this.controls.sphericalDelta) {
									this.controls.sphericalDelta.theta = 0;
									this.controls.sphericalDelta.phi = 0;
									this.controls.sphericalDelta.radius = 0;
								}
								this.controls.update();
							}
						} catch (error) {
							// 回退：不做处理
						}
						break;
					
					
					case 4:	// 恢复位置旋转：切换时姿态不变但control后跳动（不对症，无效，相当于case 0）
						const savedPosition = this.camera.position.clone();
						const savedRotation = this.camera.rotation.clone();
						this.controls.update();
						this.camera.position.copy(savedPosition);
						this.camera.rotation.copy(savedRotation);
						break;
					
					case 5:	// 重新创建控制器：切换时跳动，保持位置和目标，但spherical归0（大消耗）
						this.controls.dispose();
						this.controls = new OrbitControls(this.camera, this.renderer.domElement);
						this.controls.target.copy(correctedTarget);
						this.controls.update();
						break;
				}
			}

			toggleAutoAddKeyframe() {
				// 仅在自定义相机模式下且相机动画未启用时可用
				if (this.state.cameras.currentType !== 'custom' || this.state.cameraAnim.isEnabled) {
					return;
				}
				
				this.state.autoAddKeyframeEnabled = !this.state.autoAddKeyframeEnabled;
				this.updateAutoAddKeyframeButtonState();
			}

			toggleOrthographic() {
				// 对场景相机和默认正交相机禁用
				const isSceneCamera = this.state.cameras.currentType === 'scene';
				
				if (isSceneCamera) {
					this.dom.toggles.ortho.checked = this.camera.isOrthographicCamera;
					return;
				}
				
				const isOrtho = this.dom.toggles.ortho.checked;
				const currentCamera = this.camera;
				const container = this.dom.container;
				const aspect = container.clientWidth / container.clientHeight;
				
				let newCamera;
				let calculatedViewHeight = null;
				
				// 获取当前相机的 roll 角度
				const currentRollAngle = currentCamera.userData.rollAngle || 0;
				
				if (isOrtho) {
					// 透视→正交
					const fov = currentCamera.fov;
					const distance = currentCamera.position.distanceTo(this.controls.target);
					const viewHeight = this.calculateViewHeightFromFov(fov, distance);
					calculatedViewHeight = viewHeight;
					
					newCamera = new THREE.OrthographicCamera(
						-viewHeight * aspect / 2,
						viewHeight * aspect / 2,
						viewHeight / 2,
						-viewHeight / 2,
						currentCamera.near,
						currentCamera.far
					);
					
					newCamera.userData.viewHeight = viewHeight;
					newCamera.userData.initialViewHeight = viewHeight;
					newCamera.userData.actualZoomFactor = 1.0;
					
				} else {
					// 正交→透视
					const viewHeight = currentCamera.userData.viewHeight || (currentCamera.top - currentCamera.bottom);
					const distance = currentCamera.position.distanceTo(this.controls.target);
					const fov = this.calculateFovFromViewHeight(viewHeight, distance);
					
					newCamera = new THREE.PerspectiveCamera(
						fov,
						aspect,
						currentCamera.near,
						currentCamera.far
					);
					
					if (newCamera.userData) {
						delete newCamera.userData.actualZoomFactor;
					}
				}
				
				newCamera.position.copy(currentCamera.position);
				newCamera.rotation.copy(currentCamera.rotation);
				newCamera.name = currentCamera.name;
				
				newCamera.userData = {
					...currentCamera.userData,
					isDefault: currentCamera.userData?.isDefault,
					creationPose: currentCamera.userData?.creationPose,
					viewHeight: isOrtho ? calculatedViewHeight : currentCamera.userData?.viewHeight,
					initialViewHeight: isOrtho ? calculatedViewHeight : currentCamera.userData?.initialViewHeight,
					actualZoomFactor: isOrtho ? 1.0 : undefined,
					rollAngle: currentRollAngle,
					near: newCamera.near,
					far: newCamera.far
				};
				
				this.camera = newCamera;
				this.controls.object = this.camera;
				
				const replaceInArray = (array) => {
					const idx = array.findIndex(c => c.name === currentCamera.name);
					if (idx >= 0) array[idx] = newCamera;
				};
				
				if (this.state.cameras.currentType === 'default') {
					replaceInArray(this.state.cameras.default);
				} else if (this.state.cameras.currentType === 'custom') {
					replaceInArray(this.state.cameras.custom);
				}
				
				/* if (currentRollAngle !== 0) {
					this.applyRollAngleToCamera(newCamera, currentRollAngle, true);
				} */
				
				setTimeout(() => {
					this.updateCameraUIForMode();
					this.onWindowResize();
					this.controls.update();
				}, 0);
				
				this.saveCurrentCameraState();
			}

			updateOrthoToggleState() {
				const orthoToggle = this.dom.toggles.ortho;
				
				if (!orthoToggle) return;
				
				const isSceneCamera = this.state.cameras.currentType === 'scene';
				const isCustomCameraWithAnim = this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled;
				const isCustomCameraWithKeyframes = this.state.cameras.currentType === 'custom' && 
												  this.camera.userData.keyframes && 
												  this.camera.userData.keyframes.length > 0;
				
				// 应该禁用的条件：场景相机、自定义相机动画启用、自定义相机有关键帧
				const shouldDisable = isSceneCamera || isCustomCameraWithAnim || isCustomCameraWithKeyframes;
				
				// 应用状态
				orthoToggle.disabled = shouldDisable;
				orthoToggle.checked = this.camera.isOrthographicCamera;
				
				if (shouldDisable) {
					orthoToggle.classList.add('disabled-control');
					orthoToggle.classList.remove('enabled-control');
				} else {
					orthoToggle.classList.remove('disabled-control');
					orthoToggle.classList.add('enabled-control');
				}
			}

			updateAutoAddKeyframeButtonState() {
				const btn = this.dom.btns.autoKeyframe;
				if (!btn) return;
				
				const isCustomCamera = this.state.cameras.currentType === 'custom';
				const isCameraAnimEnabled = this.state.cameraAnim.isEnabled;
				
				if (isCustomCamera && !isCameraAnimEnabled) {
					// 自定义相机且相机动画停用：根据 autoAddKeyframeEnabled 显示状态
					btn.disabled = false;
					btn.classList.remove('disabled-control');
					btn.classList.add('enabled-control');
					
					if (this.state.autoAddKeyframeEnabled) {
						// 启用状态：橙色背景
						btn.style.background = '#ffaa00';
						btn.title = 'Auto Add Keyframe (Enabled)';
					} else {
						// 停用状态：原色背景
						btn.style.background = '';
						btn.title = 'Auto Add Camera Keyframe';
					}
				} else if (isCustomCamera && isCameraAnimEnabled) {
					// 自定义相机且相机动画启用：禁用按钮
					btn.disabled = true;
					btn.classList.add('disabled-control');
					btn.classList.remove('enabled-control');
					btn.style.background = '';
					btn.title = 'Auto Add Camera Keyframe (Camera Animation Enabled)';
				} else {
					// 非自定义相机：始终禁用，但保持 autoAddKeyframeEnabled 值
					btn.disabled = true;
					btn.classList.add('disabled-control');
					btn.classList.remove('enabled-control');
					btn.style.background = '';
					btn.title = 'Auto Add Camera Keyframe (Only for Custom Camera)';
				}
			}

			updateKeyframeButtonsState() {
				const { 
					addCamKey, delCamKey, clearCamKey, toggleCamAnim, 
					resetCamera, deleteCustomCamera, newCamera, 
					autoKeyframe, prevKey, nextKey, yup,
					centerToObject, focusToObject
				} = this.dom.btns;
				
				const type = this.state.cameras.currentType;
				
				// 是否为自定义相机
				const isCustomCamera = type === 'custom';
				const isCameraAnimEnabled = this.state.cameraAnim.isEnabled;
				
				// 根据相机类型和相机动画状态设置按钮可用性
				const isKeyframeEnabled = isCustomCamera && !isCameraAnimEnabled;
				const isDeleteCustomEnabled = isCustomCamera && !isCameraAnimEnabled;
				const isResetEnabled = type === 'default' || (isCustomCamera && !isCameraAnimEnabled);
				const isNewCameraEnabled = true; 
				const isYupEnabled = !isCameraAnimEnabled && type !== 'scene';
				const isCenterToObjectEnabled = type === 'default' || (isCustomCamera && !isCameraAnimEnabled);
				const isFocusToObjectEnabled = type === 'default' || (isCustomCamera && !isCameraAnimEnabled);
				
				const applyButtonState = (button, shouldEnable) => {
					if (!button) return;
					
					if (shouldEnable) {
						// 启用状态
						button.disabled = false;
						button.classList.remove('disabled-control');
						button.classList.add('enabled-control');
					} else {
						// 禁用状态
						button.disabled = true;
						button.classList.remove('enabled-control');
						button.classList.add('disabled-control');
					}
				};
				
				// 设置按钮基本状态
				applyButtonState(newCamera, isNewCameraEnabled);
				applyButtonState(addCamKey, isKeyframeEnabled);
				applyButtonState(delCamKey, isKeyframeEnabled);
				applyButtonState(clearCamKey, isKeyframeEnabled);
				applyButtonState(deleteCustomCamera, isDeleteCustomEnabled);
				applyButtonState(resetCamera, isResetEnabled);
				applyButtonState(yup, isYupEnabled);
				applyButtonState(centerToObject, isCenterToObjectEnabled);
				applyButtonState(focusToObject, isFocusToObjectEnabled);
				
				// 前后关键帧按钮只在自定义相机且相机动画未启用时可用
				applyButtonState(prevKey, isCustomCamera);
				applyButtonState(nextKey, isCustomCamera);
				
				// 特殊处理 toggle-cam-anim 按钮
				if (toggleCamAnim) {
					if (isCustomCamera) {
						// 自定义相机：根据 cameraAnim.isEnabled 显示状态
						toggleCamAnim.disabled = false;
						toggleCamAnim.classList.remove('disabled-control');
						toggleCamAnim.classList.add('enabled-control');
						
						if (isCameraAnimEnabled) {
							// 启用状态：橙色背景
							toggleCamAnim.style.background = '#ffaa00';
							toggleCamAnim.title = 'Switch to Edit Mode';
						} else {
							// 停用状态：蓝色背景
							toggleCamAnim.style.background = '#4a9eff';
							toggleCamAnim.title = 'Switch to Play Mode';
						}
					} else {
						// 非自定义相机：始终禁用
						toggleCamAnim.disabled = true;
						toggleCamAnim.classList.add('disabled-control');
						toggleCamAnim.classList.remove('enabled-control');
						toggleCamAnim.style.background = '';
						toggleCamAnim.title = 'Switch to Play Mode (Only for Custom Camera)';
					}
				}
				
				this.updateAutoAddKeyframeButtonState();
				this.updateCameraControlsState();
			}

			updateCameraControlsState() {
				const isSceneCamera = this.state.cameras.currentType === 'scene';
				const isCameraAnimEnabled = this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled;
				
				const setEnabled = (el, enabled) => {
					if (!el) return;
					
					if (enabled) {
						el.classList.remove('disabled-control');
						el.classList.add('enabled-control');
						el.disabled = false;
					} else {
						el.classList.add('disabled-control');
						el.classList.remove('enabled-control');
						el.disabled = true;
					}
				};
				
				// 如果相机动画启用，禁用所有相机参数控制
				if (isCameraAnimEnabled) {
					setEnabled(this.dom.inputs.fov, false);
					setEnabled(this.dom.inputs.near, false);
					setEnabled(this.dom.inputs.far, false);
					setEnabled(this.dom.inputs.rollAngle, false);
					setEnabled(this.dom.toggles.ortho, false);
					setEnabled(this.dom.btns.resetCamera, false);
					setEnabled(this.dom.btns.centerToObject, false);
					setEnabled(this.dom.btns.focusToObject, false);
					
				} else {
					// 否则根据相机类型设置
					setEnabled(this.dom.inputs.fov, !isSceneCamera);
					setEnabled(this.dom.inputs.near, !isSceneCamera);
					setEnabled(this.dom.inputs.far, !isSceneCamera);
					setEnabled(this.dom.inputs.rollAngle, !isSceneCamera);
					setEnabled(this.dom.toggles.ortho, !isSceneCamera);
					setEnabled(this.dom.labels.keyCount, !isSceneCamera);
					setEnabled(this.dom.btns.centerToObject, !isSceneCamera);
					setEnabled(this.dom.btns.focusToObject, !isSceneCamera);
				}
				this.updateOrthoToggleState();
			}

			updateUIValuesFromCustomCamera() {
				// 只有场景相机和自定义相机动画启用时才更新
				if (this.state.cameras.currentType === 'scene' || (this.state.cameras.currentType == 'custom' && this.state.cameraAnim.isEnabled)) {
					if (this.dom.inputs.fov) {
						if (this.camera.isOrthographicCamera) {
							// 正交相机：显示viewHeight
							const viewHeight = this.camera.userData.viewHeight || (this.camera.top - this.camera.bottom);
							this.dom.inputs.fov.value = viewHeight.toFixed(2);
						} else {
							// 透视相机：显示FOV
							this.dom.inputs.fov.value = this.camera.fov.toFixed(2);
						}
					}
					
					if (this.dom.inputs.rollAngle) {
						const rollAngle = this.camera.userData.rollAngle || 0;
						this.dom.inputs.rollAngle.value = rollAngle.toFixed(2);
					}
				}
			}

			updateCameraFOV() {
				// 对场景相机禁用
				if (this.state.cameras.currentType === 'scene') {
					this.updateCameraUIForMode();
					return;
				}
				
				const input = this.dom.inputs.fov;
				const value = parseFloat(input.value);
				
				if (this.camera.isOrthographicCamera) {
					if (value < 0 || value > 1000) return;
				} else {
					if (value < 0.01 || value > 179.99) return;
				}
				
				if (this.camera.isOrthographicCamera) {
					this.updateOrthographicFromViewHeight(this.camera, value);
					this.camera.userData.viewHeight = value;
					
					const initialViewHeight = this.camera.userData.creationPose?.initialViewHeight || 
											  this.camera.userData.initialViewHeight || 10;
					if (initialViewHeight && value > 0) {
						this.camera.userData.actualZoomFactor = initialViewHeight / value;
					}
				} else {
					this.camera.fov = value;
				}
				
				this.camera.updateProjectionMatrix();
				this.saveCurrentCameraState();
			}

			updateCameraNear() {
				// 对场景相机禁用
				if (this.state.cameras.currentType === 'scene') {
					this.updateCameraUIForMode();
					return;
				}
				
				const input = this.dom.inputs.near;
				const value = parseFloat(input.value);
				
				if (value < 0.01 || value > 5000) return;
				
				this.camera.near = value;
				this.camera.updateProjectionMatrix();
				this.saveCurrentCameraState();
				
				// 动态更新 far 的最小值
				const farInput = this.dom.inputs.far;
				const minFar = value + 0.01;
				farInput.min = minFar.toFixed(2);
				
				if (parseFloat(farInput.value) < minFar) {
					farInput.value = minFar.toFixed(2);
					this.applyNumericInput({ target: farInput }, 'far');
				}
			}

			updateCameraFar() {
				// 对场景相机禁用
				if (this.state.cameras.currentType === 'scene') {
					this.updateCameraUIForMode();
					return;
				}
				
				const input = this.dom.inputs.far;
				const value = parseFloat(input.value);
				const nearValue = parseFloat(this.dom.inputs.near.value);
				const minFar = nearValue + 0.01;
				
				if (value < minFar || value > 5000) return;
				
				this.camera.far = value;
				this.camera.updateProjectionMatrix();
				this.saveCurrentCameraState();
			}

			updateCameraUIForMode() {
				const isOrtho = this.camera.isOrthographicCamera;
				const fovInput = this.dom.inputs.fov;
				
				// 检查相机类型
				const isSceneCamera = this.state.cameras.currentType === 'scene';
				const isCustomCameraWithAnim = this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled;
				
				// 使用CSS类控制状态
				const setEnabledState = (el, enabled) => {
					if (!el) return;
					
					if (enabled) {
						el.classList.remove('disabled-control');
						el.classList.add('enabled-control');
						el.disabled = false;
					} else {
						el.classList.add('disabled-control');
						el.classList.remove('enabled-control');
						el.disabled = true;
					}
				};
				
				if (isSceneCamera) {
					// 场景相机：禁用所有标签
					setEnabledState(this.dom.labels.keyCount, false);
					setEnabledState(this.dom.labels.ortho, false);
					setEnabledState(this.dom.labels.fov, false);
					setEnabledState(this.dom.labels.clip, false);
					setEnabledState(this.dom.labels.roll, false);
				} else {
					// 非场景相机：启用所有标签
					setEnabledState(this.dom.labels.keyCount, true);
					setEnabledState(this.dom.labels.ortho, true);
					setEnabledState(this.dom.labels.fov, true);
					setEnabledState(this.dom.labels.clip, true);
					setEnabledState(this.dom.labels.roll, true);
				}
				
				if (isSceneCamera || isCustomCameraWithAnim) {
					// 场景相机或自定义相机播放模式：禁用所有输入控件和按钮
					const controlsToDisable = [
						this.dom.inputs.fov,
						this.dom.inputs.near,
						this.dom.inputs.far,
						this.dom.toggles.ortho,
						this.dom.btns.resetCamera,
						this.dom.inputs.rollAngle,
						this.dom.btns.yup
					];
					
					controlsToDisable.forEach(control => {
						setEnabledState(control, false);
					});
					
				} else {
					// 默认相机和自定义相机编辑模式：启用所有控件
					const controlsToEnable = [
						this.dom.inputs.fov,
						this.dom.inputs.near,
						this.dom.inputs.far,
						this.dom.btns.resetCamera,
						this.dom.inputs.rollAngle,
						this.dom.btns.yup
					];
					
					controlsToEnable.forEach(control => {
						setEnabledState(control, true);
					});
				}
				
				// 确保正交复选框状态正确
				if (this.dom.toggles.ortho) {
					this.dom.toggles.ortho.checked = isOrtho;
				}
				
				// 更新 FOV/Size 输入框
				if (isOrtho) {
					this.dom.labels.fov.textContent = "Size";
					fovInput.min = 0.01;
					fovInput.max = 1000;
					fovInput.step = 0.01;
					
					// 优先从userData读取viewHeight
					let viewHeight;
					if (this.camera.userData.viewHeight !== undefined) {
						viewHeight = this.camera.userData.viewHeight;
					} else {
						viewHeight = this.camera.top - this.camera.bottom;
						this.camera.userData.viewHeight = viewHeight;
					}
					
					fovInput.value = viewHeight.toFixed(2);
				} else {
					this.dom.labels.fov.textContent = "FOV";
					fovInput.min = 0.01;
					fovInput.max = 179.99;
					fovInput.step = 0.01;
					fovInput.value = this.camera.fov.toFixed(2);
				}
			}

			updateOrthographicFromViewHeight(camera, viewHeight) {
				if (!camera.isOrthographicCamera) return;
				
				const container = this.dom.container;
				const aspect = container.clientWidth / container.clientHeight;
				
				// 强制camera.zoom = 1.0
				if (camera.zoom !== 1.0) {
					camera.zoom = 1.0;
				}
				
				// 不修改initialViewHeight，它应该恒定不变
				camera.left = -viewHeight * aspect / 2;
				camera.right = viewHeight * aspect / 2;
				camera.top = viewHeight / 2;
				camera.bottom = -viewHeight / 2;
				camera.userData.viewHeight = viewHeight;
				
				camera.updateProjectionMatrix();
			}

			getCurrentCamera() { 
				const val = this.dom.inputs.views.value; 
				
				// 在默认相机中查找
				const defaultCam = this.state.cameras.default.find(c => c.name === val);
				if (defaultCam) return defaultCam;
				
				// 在自定义相机中查找
				const customCam = this.state.cameras.custom.find(c => c.name === val);
				if (customCam) return customCam;
				
				// 在场景相机中查找
				const sceneCam = this.state.cameras.scene.find(c => c.name === val);
				if (sceneCam) return sceneCam;
				
				// 如果都没找到，返回第一个默认相机
				return this.state.cameras.default[0];
			}

			updateViewsMenu() {
				const select = this.dom.inputs.views;
				const current = select.value;
				
				while (select.options.length > 0) select.remove(0);
				
				const addOpt = (c, color) => {
					const opt = document.createElement('option');
					opt.value = c.name;
					opt.textContent = c.name;
					opt.style.color = color;
					if (current === c.name) {
						select.style.color = color;
					}
					select.appendChild(opt);
				};
				
				this.state.cameras.default.forEach(c => addOpt(c, "#ffffff"));
				this.state.cameras.custom.forEach(c => addOpt(c, "#ffaa00"));
				this.state.cameras.scene.forEach(c => addOpt(c, "#00ff00"));
				
				if (current && Array.from(select.options).some(o => o.value === current)) {
					select.value = current;
				} else if (select.options.length) {
					select.value = select.options[0].value;
				}
				
				// 更新select元素的颜色
				this.updateSelectColor();
			}

			handleViewChange(e) {
				const val = e.target.value;
				let cam = this.state.cameras.default.find(c => c.name === val) || 
						 this.state.cameras.custom.find(c => c.name === val) || 
						 this.state.cameras.scene.find(c => c.name === val);
				
				if (cam) {
					this.switchToCamera(cam);
					this.dom.inputs.views.value = val;
					
					// 更新select元素的颜色
					this.updateSelectColor();
					
					this.updateCameraUIForMode();
				}
			}

			updateSelectColor() {
				const select = this.dom.inputs.views;
				if (!select) return;
				
				const selectedCamera = this.getCurrentCamera();
				if (!selectedCamera) {
					select.style.color = "#ffffff"; // 默认白色
					return;
				}
				
				// 根据相机类型设置颜色
				if (this.state.cameras.default.includes(selectedCamera)) {
					select.style.color = "#ffffff"; // 默认相机：白色
				} else if (this.state.cameras.custom.includes(selectedCamera)) {
					select.style.color = "#ffaa00"; // 自定义相机：橙色
				} else if (this.state.cameras.scene.includes(selectedCamera)) {
					select.style.color = "#00ff00"; // 场景相机：绿色
				} else {
					select.style.color = "#ffffff"; // 其他情况：白色
				}
			}

			handleCameraWheel(event) {
				// 对场景相机和启用动画的自定义相机禁用滚轮交互
				const isSceneCamera = this.state.cameras.currentType === 'scene';
				const isCustomCameraWithAnim = this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled;
				
				if (isSceneCamera || isCustomCameraWithAnim) {
					event.preventDefault();
					return;
				}
				
				event.preventDefault();
				const camera = this.camera;
				const controls = this.controls;
				
				const zoomSpeed = 0.05;
				const deltaFactor = 1 + (event.deltaY < 0 ? zoomSpeed : -zoomSpeed);
				
				const MIN_ZOOM_FACTOR = 0.01;
				const MAX_ZOOM_FACTOR = 1000.0;
				
				if (camera.userData.actualZoomFactor === undefined) {
					camera.userData.actualZoomFactor = 1.0;
				}
				
				const oldZoomFactor = camera.userData.actualZoomFactor;
				const newZoomFactor = oldZoomFactor * deltaFactor;
				const clampedZoomFactor = Math.max(MIN_ZOOM_FACTOR, Math.min(MAX_ZOOM_FACTOR, newZoomFactor));
				camera.userData.actualZoomFactor = clampedZoomFactor;
				
				if (camera.isOrthographicCamera) {
					let initialViewHeight;
					const isFixedView = camera.userData.isDefault && camera.userData.fixedView;
					
					if (camera.isFixedView) {
						// 对于默认正交相机，使用 initialViewHeight
						initialViewHeight = camera.userData.initialViewHeight || 
										   (camera.top - camera.bottom) || 10;
					} else {
						// 对于透视相机，使用保存的 initialViewHeight
						initialViewHeight = camera.userData.initialViewHeight || 
										   camera.userData.creationPose?.initialViewHeight || 10;
					}
					
					const newViewHeight = initialViewHeight / clampedZoomFactor;
					const clampedViewHeight = Math.max(0.01, Math.min(1000, newViewHeight));
					
					this.updateOrthographicFromViewHeight(camera, clampedViewHeight);
					if (this.dom.inputs.fov) {
						this.dom.inputs.fov.value = clampedViewHeight.toFixed(2);
					}
				} else {
					const oldDistance = camera.position.distanceTo(controls.target);
					const deltaDistance = event.deltaY > 0 ? oldDistance * 0.1 : -oldDistance * 0.1;
					const newDistance = Math.max(0.1, oldDistance + deltaDistance);
					const direction = new THREE.Vector3();
					camera.getWorldDirection(direction);
					
					camera.position.copy(controls.target).add(direction.multiplyScalar(-newDistance));
					camera.lookAt(controls.target);
				}
				
				if (camera.zoom !== 1.0) {
					camera.zoom = 1.0;
					camera.updateProjectionMatrix();
				}
				
				this.saveCurrentCameraState();
				this.onWindowResize();
			}

			// 相机动画姿态
			updateAllSceneCameraPose(frame) {
				const { cameras } = this.state;
				
				// 遍历所有场景相机
				cameras.scene.forEach(camera => {
					if (!camera) return;
					
					// 检查是否是场景相机且有动画关键帧
					if (camera.userData.animationKeyframes && camera.userData.animationKeyframes.length > 0) {
						const frameIndex = this.getKeyframeIndex(camera, frame);
						const keyframe = camera.userData.animationKeyframes[frameIndex];
						
						if (keyframe) {
							camera.position.copy(keyframe.position);
							camera.rotation.copy(keyframe.rotation);
							camera.fov = keyframe.fov;
							camera.updateProjectionMatrix();
							
							// 应用roll角（如果关键帧中有）
							if (keyframe.roll !== undefined) {
								camera.userData.rollAngle = keyframe.roll;
							}
							
							// 对于目标相机，更新目标位置
							if (camera.userData.cameraType === 'target' && camera.userData.targetNode) {
								// 检查目标节点是否有动画关键帧
								if (camera.userData.targetNode.userData.animationKeyframes && 
									camera.userData.targetNode.userData.animationKeyframes.length > 0) {
									
									// 获取当前帧的目标点关键帧索引
									const targetFrameIndex = this.getKeyframeIndex(camera.userData.targetNode, frame);
									const targetKeyframe = camera.userData.targetNode.userData.animationKeyframes[targetFrameIndex];
									
									if (targetKeyframe) {
										// 修复：安全地获取目标位置
										let targetPosition;
										if (targetKeyframe.position && targetKeyframe.position.clone && typeof targetKeyframe.position.clone === 'function') {
											// 已经是THREE.Vector3
											targetPosition = targetKeyframe.position.clone();
										} else if (targetKeyframe.position && Array.isArray(targetKeyframe.position) && targetKeyframe.position.length >= 3) {
											// 从数组创建Vector3
											targetPosition = new THREE.Vector3(
												targetKeyframe.position[0],
												targetKeyframe.position[1],
												targetKeyframe.position[2]
											);
										} else if (targetKeyframe.position && targetKeyframe.position.x !== undefined) {
											// 从普通对象创建Vector3
											targetPosition = new THREE.Vector3(
												targetKeyframe.position.x,
												targetKeyframe.position.y,
												targetKeyframe.position.z
											);
										} else {
											// 使用当前位置
											targetPosition = camera.userData.targetNode.position.clone();
										}
										
										// 更新目标点位置
										camera.userData.targetPosition = targetPosition;
										camera.userData.targetNode.position.copy(targetPosition);
										
										// 重新计算相机朝向目标点的旋转
										const lookAtResult = this.applyLookAt(camera, targetPosition, 'camera', {
											onlyCalculate: true
										});
										
										// 应用新的旋转到相机
										camera.rotation.copy(lookAtResult.rotation);
										camera.quaternion.setFromEuler(lookAtResult.rotation);
										
										// 同时更新动画关键帧中的旋转数据
										const cameraFrameIndex = this.getKeyframeIndex(camera, frame);
										if (camera.userData.animationKeyframes && 
											cameraFrameIndex < camera.userData.animationKeyframes.length) {
											camera.userData.animationKeyframes[cameraFrameIndex].rotation.copy(lookAtResult.rotation);
										}
									}
								}
							}
							
							camera.updateMatrixWorld(true);
							camera.updateProjectionMatrix();
							
							// 虽然场景相机并不需要控制
							// 但是如果是基于现状创建自定义相机，还是需要更新control target
							if (this.state.cameras.currentType === 'scene' && this.camera === camera) {
								if (camera.userData.targetPosition) {
									this.controls.target.copy(camera.userData.targetPosition);
								} else {
									// 自由相机：根据相机方向计算前方点
									const correctedTarget = this.ControlTargetPosCorrection();
									this.syncControlsFromCamera(0, correctedTarget);
								}
							}
						}
					// 这只是保险，因为经过预处理后，至少一个关键帧
					} else {
						// 无动画：使用相机当前位置和方向
						if (camera.userData.targetPosition) {
							this.controls.target.copy(camera.userData.targetPosition);
						} else {
							// 自由相机：根据相机方向计算前方点
							const correctedTarget = this.ControlTargetPosCorrection();
							this.syncControlsFromCamera(0, correctedTarget);
						}
					}
				});
			}

			updateAllCustomCameraPose(currentFrame) {
				this.state.cameras.custom.forEach(camera => {
					// 编辑模式下，当前活跃相机保持静止
					if (camera === this.camera && 
						this.state.cameras.currentType === 'custom' && 
						!this.state.cameraAnim.isEnabled) {
						return;  
					}
					
					// 检查是否有动画关键帧
					const keyframes = camera.userData.keyframes;
					if (!keyframes || keyframes.length === 0) {
						return;
					}
					
					// 使用通用的插值函数获取相机姿态
					const interpolated = this.getCameraPose(
						keyframes,
						currentFrame, {
							includeControlsTarget: false,
							includeRoll: false,
							includeFov: false
						}
					);
					
					if (!interpolated) return;
					
					// 应用插值结果到相机
					camera.position.copy(interpolated.position);
					camera.rotation.copy(interpolated.rotation);
					
					camera.updateProjectionMatrix();
				});
			}

			updateCurrentCustomCameraPose(frame) {
				const keyframes = this.state.cameraAnim.keyframes;
				
				const interpolated = this.getCameraPose(
					keyframes,
					frame,
					{
						includeControlsTarget: true,
						includeRoll: true,
						includeFov: true
					}
				);
				
				if (!interpolated) return;
				
				// 应用插值结果到相机
				this.camera.position.copy(interpolated.position);
				this.camera.rotation.copy(interpolated.rotation);
				
				// 根据相机类型应用不同的参数
				if (this.camera.isOrthographicCamera) {
					// 正交相机：应用viewHeight
					const viewHeight = interpolated.fov;
					this.updateOrthographicFromViewHeight(this.camera, viewHeight);
					this.camera.userData.viewHeight = viewHeight;
				} else {
					// 透视相机：应用FOV
					this.camera.fov = interpolated.fov;
				}
				
				this.camera.updateProjectionMatrix();
				
				// 更新控制目标
				if (interpolated.controlsTarget) {
					this.controls.target.copy(interpolated.controlsTarget);
					this.camera.userData.controlsTarget = interpolated.controlsTarget.clone();
				}
				
				// 应用roll角度
				if (interpolated.roll !== undefined) {
					this.camera.userData.rollAngle = interpolated.roll;
					
					// 直接使用up vector关键帧差值，不用再apply roll angle
					// 默认两者都用catmullRom插值，虽有误差，但效率更高
					/* this.applyRollAngleToCamera(this.camera, interpolated.roll, false); */
				}
				
				// 确保 upVector 保存到相机 userData
				if (!this.camera.userData.upVector) {
					this.camera.userData.upVector = this.camera.up.clone();
				}
			}

			getCameraPose(keyframes, frame, options = {}) {
				if (!keyframes || !keyframes.length) {
					return null;
				}
				
				const {
					includeControlsTarget = false,
					includeRoll = false,
					includeFov = false,
					fovInterpolation = 'catmull-rom',	// or any for linear
					rollInterpolation = 'catmull-rom'	// or any for linear
				} = options;
				
				// 统一声明 result 变量
				let result = null;
				
				// 检测关键帧的投影类型
				let defaultOrthographic = false;
				if (keyframes.length > 0) {
					defaultOrthographic = keyframes[0].isOrthographic || false;
				}
				
				// 处理边界情况：单个关键帧、帧在第一个之前、帧在最后一个之后
				if (keyframes.length === 1 || frame <= keyframes[0].frame) {
					const k = keyframes[0];
					return this.getCameraPoseFromKeyframe(k, includeControlsTarget, includeFov, includeRoll, defaultOrthographic);
				}
				
				if (frame >= keyframes[keyframes.length - 1].frame) {
					const k = keyframes[keyframes.length - 1];
					return this.getCameraPoseFromKeyframe(k, includeControlsTarget, includeFov, includeRoll, defaultOrthographic);
				}
				
				// 找到当前帧所在的关键帧区间
				let prevKeyframe = null, nextKeyframe = null;
				
				for (let k of keyframes) {
					if (k.frame <= frame) prevKeyframe = k;
					if (k.frame >= frame && !nextKeyframe) nextKeyframe = k;
				}
				
				// 正好在关键帧上
				if (prevKeyframe && prevKeyframe.frame === frame) {
					return this.getCameraPoseFromKeyframe(prevKeyframe, includeControlsTarget, includeFov, includeRoll, defaultOrthographic);
				}
				
				// 在两个关键帧之间进行插值
				if (prevKeyframe && nextKeyframe && prevKeyframe.frame !== nextKeyframe.frame) {
					const t = (frame - prevKeyframe.frame) / (nextKeyframe.frame - prevKeyframe.frame);
					const prevIndex = keyframes.indexOf(prevKeyframe);
					const nextIndex = keyframes.indexOf(nextKeyframe);
					const p0Index = Math.max(0, prevIndex - 1);
					const p3Index = Math.min(keyframes.length - 1, nextIndex + 1);
					const p0 = keyframes[p0Index];
					const p3 = keyframes[p3Index];
					
					// 位置插值（Catmull-Rom）
					const position = this.catmullRomInterpolateVector3(
						t,
						p0.position,
						prevKeyframe.position,
						nextKeyframe.position,
						p3.position
					);
					
					// 旋转插值（Catmull-Rom）
					const rotation = this.catmullRomInterpolateEuler(
						t,
						p0.rotation,
						prevKeyframe.rotation,
						nextKeyframe.rotation,
						p3.rotation
					);
					
					result = {
						position,
						rotation
					};
					
					// FOV插值（根据选项选择线性或Catmull-Rom）
					if (includeFov) {
						let fov;
						if (fovInterpolation === 'catmull-rom') {
							const p0Fov = p0.fov !== undefined ? p0.fov : (p0.isOrthographic ? 10 : 50);
							const p1Fov = prevKeyframe.fov !== undefined ? prevKeyframe.fov : (prevKeyframe.isOrthographic ? 10 : 50);
							const p2Fov = nextKeyframe.fov !== undefined ? nextKeyframe.fov : (nextKeyframe.isOrthographic ? 10 : 50);
							const p3Fov = p3.fov !== undefined ? p3.fov : (p3.isOrthographic ? 10 : 50);
							
							fov = this.catmullRomInterpolate(
								t,
								p0Fov,
								p1Fov,
								p2Fov,
								p3Fov
							);
							
							// 根据投影类型钳制范围
							if (defaultOrthographic) {
								// 正交相机：viewHeight范围
								fov = Math.max(0.01, Math.min(1000, fov));
							} else {
								// 透视相机：fov范围
								fov = Math.max(0.01, Math.min(179.99, fov));
							}
						} else {
							// 线性插值
							const prevFov = prevKeyframe.fov !== undefined ? prevKeyframe.fov : (prevKeyframe.isOrthographic ? 10 : 50);
							const nextFov = nextKeyframe.fov !== undefined ? nextKeyframe.fov : (nextKeyframe.isOrthographic ? 10 : 50);
							fov = prevFov + (nextFov - prevFov) * t;
						}
						result.fov = fov;
					}
					
					// 控制目标插值（Catmull-Rom）
					if (includeControlsTarget) {
						// 确保所有关键点都有有效的controlsTarget
						const p0Target = p0.controlsTarget || prevKeyframe.controlsTarget || nextKeyframe.controlsTarget;
						const p1Target = prevKeyframe.controlsTarget;
						const p2Target = nextKeyframe.controlsTarget;
						const p3Target = p3.controlsTarget || nextKeyframe.controlsTarget || prevKeyframe.controlsTarget;
						
						if (p0Target && p1Target && p2Target && p3Target) {
							// 使用Catmull-Rom插值，但检查结果的合理性
							const rawTarget = this.catmullRomInterpolateVector3(
								t,
								p0Target,
								p1Target,
								p2Target,
								p3Target
							);
							
							// 检查插值结果是否合理
							const distance = prevKeyframe.position.distanceTo(rawTarget);
							if (distance > this.state.controlTargetDist.minDist && distance < this.state.controlTargetDist.maxDist) {
								result.controlsTarget = rawTarget;
							} else {
								// 插值结果不合理，使用线性插值
								result.controlsTarget = p1Target.clone().lerp(p2Target, t);
							}
						} else if (p1Target && p2Target) {
							// 线性插值
							result.controlsTarget = p1Target.clone().lerp(p2Target, t);
						}
					}
					
					// Roll角度插值（Catmull-Rom）
					if (includeRoll) {
						const p0Roll = p0.roll !== undefined ? p0.roll : 0;
						const p1Roll = prevKeyframe.roll !== undefined ? prevKeyframe.roll : 0;
						const p2Roll = nextKeyframe.roll !== undefined ? nextKeyframe.roll : 0;
						const p3Roll = p3.roll !== undefined ? p3.roll : 0;
						
						let roll;
						if (rollInterpolation === 'catmull-rom') {
							roll = this.catmullRomInterpolateAngle(t,
								p0Roll,
								p1Roll,
								p2Roll,
								p3Roll
							);
						} else {
							roll = this.lerpAngle(
								p1Roll,
								p2Roll,
								t
							);
						}
						result.roll = roll;
					}
					return result;
				}
				return null;
			}

			getCameraPoseFromKeyframe(k, includeControlsTarget, includeFov, includeRoll, defaultOrthographic = false) {
				const result = {
					position: k.position.clone(),
					rotation: k.rotation.clone()
				};
				
				if (includeControlsTarget && k.controlsTarget) {
					result.controlsTarget = k.controlsTarget.clone();
				}
				
				if (includeFov) {
					const isOrthographic = k.isOrthographic !== undefined ? k.isOrthographic : defaultOrthographic;
					if (isOrthographic) {
						result.fov = (k.fov !== undefined) ? k.fov : 10;
						result.isOrthographic = true;
					} else {
						result.fov = (k.fov !== undefined) ? k.fov : 50;
						result.isOrthographic = false;
					}
				}
				
				if (includeRoll) {
					result.roll = (k.roll !== undefined) ? k.roll : 0;
				}
				
				if (k.upVector) {
					result.upVector = k.upVector.clone();
				} else {
					// 如果没有保存的 upVector，根据旋转计算一个
					const quaternion = new THREE.Quaternion().setFromEuler(k.rotation);
					const upVector = new THREE.Vector3(0, 1, 0);
					upVector.applyQuaternion(quaternion);
					result.upVector = upVector;
				}
				
				return result;
			}

			// 相机切换姿态
			saveCurrentCameraState() {
				if (this.camera) {
					const isOrtho = this.camera.isOrthographicCamera;
					const name = this.camera.name;
					
					// 使用 calculateCameraRollAngle 计算当前的 roll 和 up 向量
					const rollResult = this.calculateCameraRollAngle(this.camera, this.controls.target);
					const rollAngle = rollResult.roll;
					const upVector = rollResult.upVector;
					
					// 更新相机的 userData
					this.camera.userData.rollAngle = rollAngle;
					this.camera.userData.upVector = upVector.clone();
					
					// 确保 near 和 far 也保存到相机 userData
					this.camera.userData.near = this.camera.near;
					this.camera.userData.far = this.camera.far;
					
					// 始终从userData读取viewHeight作为历史值，不因当前模式而清除
					let viewHeight = null;
					if (this.camera.userData.viewHeight !== undefined && this.camera.userData.viewHeight !== null) {
						viewHeight = this.camera.userData.viewHeight;
					} else if (isOrtho) {
						// 只有确实没有时，才从相机读取（仅初始化场景相机时）
						viewHeight = this.camera.top - this.camera.bottom;
						this.camera.userData.viewHeight = viewHeight;
					}
					
					this.state.cameras.states.set(name, {
						position: this.camera.position.clone(),
						rotation: this.camera.rotation.clone(),
						fov: this.camera.fov,
						near: this.camera.near,
						far: this.camera.far,
						zoom: this.camera.zoom || 1,
						controlsTarget: this.controls.target.clone(),
						orthographic: isOrtho,
						viewHeight: viewHeight,
						rollAngle: rollAngle,
						up: upVector
					});
				}
			}

			getCurrentCameraState(camera) {
				const currentFrame = Math.floor(this.state.playback.currentFrame);
				const state = {
					position: new THREE.Vector3(),
					rotation: new THREE.Euler(),
					fov: 50,
					near: 0.1,
					far: 100,
					isOrthographic: false,
					viewHeight: null,
					initialDistance: null,
					controlsTarget: new THREE.Vector3(),
					up: new THREE.Vector3(0, 1, 0),
					rollAngle: 0
				};
				
				// 获取相机基本信息
				state.isOrthographic = camera.isOrthographicCamera;
				
				if (state.isOrthographic) {
					state.viewHeight = camera.top - camera.bottom;
					if (camera.userData && camera.userData.viewHeight) {
						state.viewHeight = camera.userData.viewHeight;
					}
				} else {
					// 对于透视相机，计算到目标的初始距离
					if (this.controls && this.controls.target) {
						state.initialDistance = camera.position.distanceTo(this.controls.target);
					}
				}
				
				// 根据相机类型获取当前帧的姿态
				if (this.state.cameras.currentType === 'scene') {
					// 场景相机：从动画关键帧获取当前帧姿态
					if (camera.userData.animationKeyframes && camera.userData.animationKeyframes.length > 0) {
						const frameIndex = this.getKeyframeIndex(camera, currentFrame);
						const keyframe = camera.userData.animationKeyframes[frameIndex];
						
						if (keyframe) {
							state.position.copy(keyframe.position);
							state.rotation.copy(keyframe.rotation);
							state.fov = keyframe.fov;
							state.near = camera.near;
							state.far = camera.far;
							state.rollAngle = keyframe.roll || 0;
							
							// 关键修改：优先使用关键帧中的upVector
							if (keyframe.upVector) {
								state.up.copy(keyframe.upVector);
							} else {
								// 如果没有存储upVector，则根据旋转计算
								const quaternion = new THREE.Quaternion().setFromEuler(keyframe.rotation);
								const upVector = new THREE.Vector3(0, 1, 0);
								upVector.applyQuaternion(quaternion);
								state.up.copy(upVector);
							}
							
							// 获取控制目标
							if (camera.userData.targetPosition) {
								state.controlsTarget.copy(camera.userData.targetPosition);
							} else {
								// 自由相机：计算前方点作为目标
								const direction = new THREE.Vector3(0, 0, -1);
								direction.applyQuaternion(camera.quaternion);
								state.controlsTarget.copy(camera.position.clone().add(direction.multiplyScalar(10)));
							}
						} else {
							// 没有关键帧，使用相机当前位置
							this.copyCurrentCameraState(camera, state);
						}
					} else {
						// 没有动画关键帧，使用相机当前位置
						this.copyCurrentCameraState(camera, state);
					}
				} else {
					// 默认相机或自定义相机：直接使用当前状态
					this.copyCurrentCameraState(camera, state);
				}
				
				return state;
			}

			copyCurrentCameraState(camera, state) {
				state.position.copy(camera.position);
				state.rotation.copy(camera.rotation);
				state.fov = camera.fov;
				state.near = camera.near;
				state.far = camera.far;
				
				// 使用calculateCameraRollAngle获取roll角和up vector
				const rollResult = this.calculateCameraRollAngle(camera);
				state.rollAngle = rollResult.roll;
				state.up.copy(rollResult.upVector);
				
				// 获取控制目标
				if (this.controls && this.controls.target) {
					state.controlsTarget.copy(this.controls.target);
				} else if (camera.userData && camera.userData.controlsTarget) {
					state.controlsTarget.copy(camera.userData.controlsTarget);
				} else {
					// 计算前方点作为目标
					const direction = new THREE.Vector3(0, 0, -1);
					direction.applyQuaternion(camera.quaternion);
					state.controlsTarget.copy(camera.position.clone().add(direction.multiplyScalar(10)));
				}
			}

			getCameraSavedState(camera) {
				if (camera.userData && camera.userData.targetPosition) {
					return camera.userData.targetPosition.clone();
				} else if (camera.userData && camera.userData.controlsTarget) {
					return camera.userData.controlsTarget.clone();
				} else {
					const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
					return camera.position.clone().add(dir.multiplyScalar(10));
				}
			}

			// 场景相机导入
			getTrackValueAtTime(track, time) {
				if (!track || !track.times || track.times.length === 0) return null;
				
				// 优先使用 Three.js 原生插值方法，支持所有插值类型
				if (track.getValue && typeof track.getValue === 'function') {
					try {
						return track.getValue(time);
					} catch (error) {
						/* this.showMessage("Three.js native interpolation failed: " + error.message + ", falling back to custom interpolation"); */
					}
				}
				
				// 回退到自定义插值方法
				const times = track.times;
				const values = track.values;
				
				if (time <= times[0]) {
					return this.extractValue(track, 0);
				}
				
				if (time >= times[times.length - 1]) {
					return this.extractValue(track, times.length - 1);
				}
				
				let i = 0;
				while (i < times.length - 1 && times[i] < time) i++;
				
				const prevIndex = i - 1;
				const nextIndex = i;
				const t = (time - times[prevIndex]) / (times[nextIndex] - times[prevIndex]);
				
				return this.interpolateValue(track, prevIndex, nextIndex, t);
			}

			extractValue(track, index) {
				const values = track.values;
				
				// 支持 'vector' 和 'vector3' 两种类型
				if (track.ValueTypeName === 'vector3' || track.ValueTypeName === 'vector') {
					const baseIndex = index * 3;
					// 检查数组边界
					if (baseIndex + 2 < values.length) {
						return new THREE.Vector3(values[baseIndex], values[baseIndex+1], values[baseIndex+2]);
					} else {
						/* this.showMessage("Error: Unable to extract vector value: Array index out of bounds."); */
						return null;
					}
				} else if (track.ValueTypeName === 'quaternion') {
					const baseIndex = index * 4;
					if (baseIndex + 3 < values.length) {
						return new THREE.Quaternion(values[baseIndex], values[baseIndex+1], 
													values[baseIndex+2], values[baseIndex+3]);
					} else {
						/* this.showMessage("Error: Unable to extract quaternion: Array index out of bounds."); */
						return null;
					}
				} else if (track.ValueTypeName === 'number') {
					if (index < values.length) {
						return values[index];
					} else {
						/* this.showMessage("Error: Unable to extract scalar: Array index out of bounds."); */
						return null;
					}
				}
				
				/* this.showMessage("Error: Unknown track type:" + track.ValueTypeName); */
				return null;
			}

			interpolateValue(track, prevIndex, nextIndex, t) {
				const values = track.values;
				
				// 支持 'vector' 和 'vector3' 两种类型
				if (track.ValueTypeName === 'vector3' || track.ValueTypeName === 'vector') {
					const prevIndex3 = prevIndex * 3;
					const nextIndex3 = nextIndex * 3;
					
					// 检查数组边界
					if (prevIndex3 + 2 >= values.length || nextIndex3 + 2 >= values.length) {
						/* this.showMessage("Error: Unable to interpolate vector: Array index out of bounds."); */
						return null;
					}
					
					const x = THREE.MathUtils.lerp(values[prevIndex3], values[nextIndex3], t);
					const y = THREE.MathUtils.lerp(values[prevIndex3+1], values[nextIndex3+1], t);
					const z = THREE.MathUtils.lerp(values[prevIndex3+2], values[nextIndex3+2], t);
					return new THREE.Vector3(x, y, z);
				} else if (track.ValueTypeName === 'quaternion') {
					const prevIndex4 = prevIndex * 4;
					const nextIndex4 = nextIndex * 4;
					
					if (prevIndex4 + 3 >= values.length || nextIndex4 + 3 >= values.length) {
						/* this.showMessage("Error: Unable to interpolate quaternion: Array index out of bounds."); */
						return null;
					}
					
					const q1 = new THREE.Quaternion(values[prevIndex4], values[prevIndex4+1], 
													values[prevIndex4+2], values[prevIndex4+3]);
					const q2 = new THREE.Quaternion(values[nextIndex4], values[nextIndex4+1], 
													values[nextIndex4+2], values[nextIndex4+3]);
					const result = new THREE.Quaternion();
					return result.slerpQuaternions(q1, q2, t);
				} else if (track.ValueTypeName === 'number') {
					if (prevIndex >= values.length || nextIndex >= values.length) {
						/* this.showMessage("Error: Unable to interpolate scalar: Array index out of bounds."); */
						return null;
					}
					
					return THREE.MathUtils.lerp(values[prevIndex], values[nextIndex], t);
				}
				
				/* this.showMessage("Error: Unknown track type:" + track.ValueTypeName); */
				return null;
			}

			getKeyframeIndex(object, frame, keyframeProperty = 'animationKeyframes') {
				if (!object || !object.userData || !object.userData[keyframeProperty]) {
					return 0;
				}
				
				const keyframes = object.userData[keyframeProperty];
				const totalKeyframes = keyframes.length;
				
				if (totalKeyframes === 0) {
					return 0;
				}
				
				if (frame < 0) {
					return 0;
				}
				
				const frameIndex = Math.min(Math.floor(frame), totalKeyframes - 1);
				return Math.max(0, frameIndex);
			}

			generateStaticKeyframes(camera) {
				const cameraName = camera.name;
				
				camera.userData.animationKeyframes = [];
				const totalFrames = this.state.playback.totalFrames > 1 ? this.state.playback.totalFrames : 1;
				
				for (let frame = 0; frame < totalFrames; frame++) {
					let position, rotation, fov;
					let roll = camera.userData.rollAngle || 0;
					let upVector = camera.userData.upVector.clone() || new THREE.Vector3(0, 1, 0);
					
					if (camera.userData.cameraType === "target" && camera.userData.targetPosition) {
						// 目标相机：使用目标点计算旋转
						const rotationData = this.applyLookAt(camera, camera.userData.targetPosition, "camera", { onlyCalculate: true });
						position = camera.position.clone();
						fov = camera.fov;
						
						// 创建临时相机来应用roll角
						// fbx没有提供quaternion，fbxloader也无法读出curve
						// 目前无法复现fbx格式的roll
						const tempCamera = new THREE.PerspectiveCamera();
						tempCamera.position.copy(position);
						tempCamera.quaternion.setFromEuler(rotationData.rotation);
						
						// 应用roll角到旋转中
						if (Math.abs(roll) > 0.001) {
							this.applyRollAngleToCamera(tempCamera, roll, true);
							rotation = tempCamera.rotation.clone();
						} else {
							rotation = rotationData.rotation.clone();
						}
						
					} else {
						// 自由相机：使用当前矫正后的旋转
						position = camera.position.clone();
						rotation = camera.rotation.clone();
						fov = camera.fov;
					}
					
					camera.userData.animationKeyframes.push({
						frame: frame,
						position: position,
						rotation: rotation,
						fov: fov,
						roll: camera.userData.rollAngle || 0,
						upVector: upVector.clone(),
						targetPosition: camera.userData.targetPosition ? camera.userData.targetPosition.clone() : null
					});
				}
			}

			processCameraAnimationData(camera) {
				const cameraName = camera.name;
				const hasAnimation = this.state.currentAnimations && this.state.currentAnimations.length > 0;
				
				if (!hasAnimation) {
					// 无动画：使用当前矫正后的状态作为所有关键帧
					this.generateStaticKeyframes(camera);
					return;
				}
				
				// 使用第一个动画剪辑
				const animationClip = this.state.currentAnimations[0];
				const fps = this.state.playback.fps;
				const duration = animationClip.duration;
				const totalFrames = Math.ceil(duration * fps);
				
				// 查找该相机相关的所有轨道
				const cameraTracks = animationClip.tracks.filter(track => {
					return track.name.startsWith(cameraName + ".");
				});
				
				// 查找目标节点相关的轨道
				let targetTracks = [];
				if (camera.userData.targetNode) {
					const targetName = camera.userData.targetNode.name;
					targetTracks = animationClip.tracks.filter(track => {
						return track.name.startsWith(targetName + ".");
					});
				}
				
				if (cameraTracks.length === 0 && targetTracks.length === 0) {
					this.generateStaticKeyframes(camera);
					return;
				}
				
				// 具体轨道
				const positionTrack = cameraTracks.find(t => t.name === cameraName + ".position");
				const rotationTrack = cameraTracks.find(t => t.name === cameraName + ".rotation" || t.name === cameraName + ".quaternion");
				const fovTrack = cameraTracks.find(t => t.name === cameraName + ".fov");
				const rollTrack = cameraTracks.find(t => t.name === cameraName + ".userData.roll" || t.name === cameraName + ".roll");
				
				const targetPositionTrack = targetTracks.find(t => t.name === camera.userData.targetNode?.name + ".position");
				
				// 存储关键帧
				camera.userData.animationKeyframes = [];
				camera.userData.hasAnimation = true;
				
				for (let frame = 0; frame < totalFrames; frame++) {
					const time = frame / fps;
					
					// 获取相机位置（从轨道读取或使用初始位置）
					let position;
					if (positionTrack) {
						// 获取相机位置
						const positionValue = this.getTrackValueAtTime(positionTrack, time);
						if (positionValue instanceof THREE.Vector3) {
							position = positionValue.clone();
						} else if (Array.isArray(positionValue) && positionValue.length >= 3) {
							position = new THREE.Vector3(positionValue[0], positionValue[1], positionValue[2]);
						} else {
							position = camera.position.clone();
						}
					} else {
						position = camera.position.clone();
					}
					
					// 获取目标位置
					let targetPosition = null;
					if (targetPositionTrack && camera.userData.targetNode) {
						const targetValue = this.getTrackValueAtTime(targetPositionTrack, time);
						if (targetValue instanceof THREE.Vector3) {
							targetPosition = targetValue.clone();
						} else if (Array.isArray(targetValue) && targetValue.length >= 3) {
							targetPosition = new THREE.Vector3(targetValue[0], targetValue[1], targetValue[2]);
						} else if (camera.userData.targetPosition) {
							targetPosition = camera.userData.targetPosition.clone();
						}
					} else if (camera.userData.targetPosition) {
						targetPosition = camera.userData.targetPosition.clone();
					}
					
					// 计算或获取旋转
					let rotation;
					let roll = 0;
					let upVector;
					
					if (camera.userData.cameraType === "target" && targetPosition) {
						// 目标相机：使用applyLookAt计算旋转（只计算，不应用）
						const lookAtResult = this.applyLookAt(camera, targetPosition, "camera", {
							onlyCalculate: true
						});
						
						rotation = lookAtResult.rotation.clone();
						
						// 创建临时相机来计算roll角
						// 基于动画姿态
						// fbx没有提供quaternion轨道，fbxloader也无法读出curve
						// 目前无法复现fbx格式的roll
						// const tempCamera = new THREE.PerspectiveCamera();
						// tempCamera.position.copy(position);
						// tempCamera.quaternion.setFromEuler(rotation);
						// const rollResult = this.calculateCameraRollAngle(tempCamera, targetPosition);
						roll = camera.userData.rollAngle || 0;
						upVector = camera.userData.upVector.clone();
						
						// 在预处理阶段将roll角应用到目标相机旋转中
						/* if (Math.abs(roll) > 0.001) {
							this.applyRollAngleToCamera(tempCamera, roll, true);
							rotation.copy(tempCamera.rotation);
						} */
						
					} else if (rotationTrack) {
						// 自由相机：从轨道获取旋转
						const rotationValue = this.getTrackValueAtTime(rotationTrack, time);
						let quaternion;
						
						if (rotationValue instanceof THREE.Quaternion) {
							quaternion = rotationValue.clone();
						} else if (Array.isArray(rotationValue) && rotationValue.length >= 3) {
							// 如果是欧拉角数组，转换为四元数
							const euler = new THREE.Euler(rotationValue[0], rotationValue[1], rotationValue[2]);
							quaternion = new THREE.Quaternion().setFromEuler(euler);
						} else if (rotationValue && rotationValue.x !== undefined) {
							// 如果是欧拉角对象，转换为四元数
							const euler = new THREE.Euler(rotationValue.x, rotationValue.y, rotationValue.z);
							quaternion = new THREE.Quaternion().setFromEuler(euler);
						} else {
							// 没有有效的旋转值，使用相机当前旋转
							quaternion = camera.quaternion.clone();
						}
						
						// 如果是自由相机，应用旋转矫正
						if (camera.userData.cameraType === "free" && camera.userData.fbxCorrectionQuaternion) {
							quaternion.multiply(camera.userData.fbxCorrectionQuaternion);
						}
						
						rotation = new THREE.Euler().setFromQuaternion(quaternion);
						
						// 创建临时相机来计算自由相机roll角，但无需应用，旋转姿态已包含
						const tempCamera = new THREE.PerspectiveCamera();
						tempCamera.position.copy(position);
						tempCamera.quaternion.copy(quaternion);
						
						const rollResult = this.calculateCameraRollAngle(tempCamera);
						roll = rollResult.roll;
						upVector = rollResult.upVector;
						
					} else {
						// 自由相机：没有旋转轨道，使用初始旋转
						rotation = camera.rotation.clone();
						roll = camera.userData.rollAngle || 0;
						upVector = camera.userData.upVector.clone();
					}
					
					// 获取FOV
					let fov = camera.fov;
					if (fovTrack) {
						const fovValue = this.getTrackValueAtTime(fovTrack, time);
						if (typeof fovValue === "number") {
							fov = fovValue;
						} else if (Array.isArray(fovValue) && fovValue.length > 0) {
							fov = fovValue[0];
						}
					}
					
					// 存储关键帧 - 确保数据类型正确
					camera.userData.animationKeyframes.push({
						frame: frame,
						position: position,
						rotation: rotation,
						fov: fov,
						roll: roll,
						upVector: upVector.clone(),
						targetPosition: targetPosition ? targetPosition.clone() : null
					});
				}
			}

			processTargetNodeAnimationData(targetNode) {
				// 检查是否有动画数据
				const hasAnimation = this.state.currentAnimations && this.state.currentAnimations.length > 0;
				
				if (!hasAnimation) {
					// 无动画：保存当前状态作为动画关键帧
					targetNode.userData.animationKeyframes = [{
						frame: 0,
						position: targetNode.position.clone()
					}];
					
					return;
				}
				
				// 获取动画剪辑
				const animationClip = this.state.currentAnimations[0];
				const fps = this.state.playback.fps;
				const totalFrames = Math.ceil(animationClip.duration * fps);
				
				// 创建临时场景和目标节点来模拟动画
				const tempScene = new THREE.Scene();
				const tempTarget = targetNode.clone();
				tempScene.add(tempTarget);
				
				// 创建临时动画混合器
				const tempMixer = new THREE.AnimationMixer(tempScene);
				const tempAction = tempMixer.clipAction(animationClip);
				tempAction.play();
				
				// 存储处理后的关键帧
				targetNode.userData.animationKeyframes = [];
				targetNode.userData.hasAnimation = true;
				
				let lastLogTime = Date.now();
				
				// 逐帧处理动画数据
				for (let frame = 0; frame < totalFrames; frame++) {
					// 更新时间
					const time = (frame / fps);
					tempMixer.setTime(time);
					tempMixer.update(0);
					
					// 获取当前帧的目标节点位置
					const position = tempTarget.position.clone();
					
					// 保存处理后的关键帧
					targetNode.userData.animationKeyframes.push({
						frame: frame,
						position: position
					});
				}
				
				// 清理临时资源
				tempMixer.stopAllAction();
				tempMixer.uncacheRoot(tempScene);
			}

			processSceneCameras(scene) {
				// 先清理旧场景相机的状态缓存
				this.state.cameras.scene.forEach(cam => {
					this.state.cameras.states.delete(cam.name);
				});
				
				this.state.cameras.scene.forEach(cam => {
					if (cam.userData.visualization) cam.userData.visualization.forEach(a => this.scene.remove(a));
					this.scene.remove(cam);
				});
				this.state.cameras.scene = [];
				this.state.cameras.activeScene = null;
				
				// 获取当前格式
				const currentFormat = this.state.currentFormat;
				const isGLB = currentFormat === 'glb';
				const isFBX = currentFormat === 'fbx';
				
				// 收集所有目标节点
				const targetNodes = [];
				scene.traverse(child => {
					const name = child.name ? child.name.toLowerCase() : '';
					const origName = child.userData && child.userData.originalName ? child.userData.originalName.toLowerCase() : '';
					if (name.includes('target') || name.includes('aim') || name.includes('lookat') ||
						origName.includes('target') || origName.includes('aim') || origName.includes('lookat')) {
						targetNodes.push(child);
					}
				});
				
				targetNodes.forEach(targetNode => {
					// 确保目标节点的动画数据被处理
					if (!targetNode.userData.animationKeyframes) {
						this.processTargetNodeAnimationData(targetNode);
					}
				});
				
				// 收集所有场景相机，跳过自定义相机
				const sceneCameras = [];
				scene.traverse(child => {
					if (child.name && child.name.startsWith('CustomCamJK_')) {
						return;
					}
					
					// 检查是否已经标记为跳过预处理（包括已导出的数据）
					if (child.userData && child.userData.skipPreprocessing) {
						return;
					}
					
					// 检查是否为已导出的数据
					if (child.userData && child.userData.isExportedData) {
						return;
					}
					
					if (child.isCamera) {
						sceneCameras.push(child);
					}
				});
				
				// 处理每个相机
				sceneCameras.forEach(child => {
					// 确保userData存在
					if (!child.userData) child.userData = {};
					
					// 检查是否已经有animationKeyframes（来自已导出的文件）
					if (child.userData.animationKeyframes && child.userData.animationKeyframes.length > 0) {
						// 已有预处理数据，跳过处理
						// 但仍需执行：添加相机、创建可视化等
						
						// 添加到场景相机列表
						this.state.cameras.scene.push(child);
						
						// 创建相机可视化
						this.createCameraVisualization(child, 0x00ff00);
						
						child.visible = false;
						
						// 初始化状态存储（如果还没有）
						if (!this.state.cameras.states.has(child.name)) {
							const viewHeight = child.isOrthographicCamera ? 
								(child.userData.viewHeight || (child.top - child.bottom)) : null;
							
							this.state.cameras.states.set(child.name, {
								position: child.position.clone(),
								rotation: child.rotation.clone(),
								fov: child.fov,
								near: child.near,
								far: child.far,
								zoom: child.zoom || 1,
								controlsTarget: this.controls.target.clone(),
								orthographic: child.isOrthographicCamera,
								viewHeight: viewHeight,
								rollAngle: child.userData.rollAngle || 0,
								up: child.up.clone()
							});
						}
						
						return; // 跳过后续预处理
					}
					
					const cameraName = child.name;
					
					// 对于GLB格式的透视相机，处理fov转换
					if (isGLB && child.isPerspectiveCamera) {
						const originalFov = child.fov;
						const aspectRatio = child.aspect || 1;
						
						// 假设原始fov是水平fov，转换为垂直fov
						const horizontalFovRad = originalFov * Math.PI / 180;
						const verticalFovRad = 2 * Math.atan(Math.tan(horizontalFovRad / 2) / aspectRatio);
						const verticalFovDeg = verticalFovRad * 180 / Math.PI;
						
						// 更新相机fov为垂直fov
						child.fov = verticalFovDeg;
						child.userData.originalHorizontalFov = originalFov;
						child.userData.convertedToVerticalFov = true;
						child.userData.aspectRatio = aspectRatio;
					}
					
					// 记录原始变换数据
					if (child.userData.transformData) {
						const transformData = child.userData.transformData;
						
						// 保存原始变换数据，但不用于roll angle计算
						child.userData.originalTransformData = transformData;
					}
					
					// 检查相机当前的世界变换矩阵
					child.updateMatrixWorld(true);
					const worldMatrix = child.matrixWorld;
					const position = new THREE.Vector3();
					const quaternion = new THREE.Quaternion();
					const scale = new THREE.Vector3();
					worldMatrix.decompose(position, quaternion, scale);
					
					// 将四元数转换为欧拉角查看
					const euler = new THREE.Euler().setFromQuaternion(quaternion, 'XYZ');
					
					// 记录相机的原始四元数和欧拉角
					child.userData.originalWorldQuaternion = quaternion.clone();
					child.userData.originalWorldEuler = euler.clone();
					
					// 尝试多种格式匹配目标节点名称
					let targetNode = null;
					const possibleTargetNames = [
						cameraName + 'Target',
						cameraName + 'target',
						cameraName + '.Target',
						cameraName + '.target',
						cameraName + '_Target',
						cameraName + '_target',
						'Target' + cameraName,
						'target' + cameraName,
						'Target_' + cameraName,
						'target_' + cameraName,
						cameraName.replace('Camera', 'Target'),
						cameraName.replace('camera', 'target'),
						cameraName.replace('Camera', 'Target'),
						cameraName.replace('CAMERA', 'TARGET')
					];
					
					// 尝试在目标节点中查找
					for (const targetName of possibleTargetNames) {
						targetNode = targetNodes.find(t => {
							const tName = t.name;
							const tOrig = t.userData ? t.userData.originalName : tName;
							return tName === targetName || tOrig === targetName ||
								   tName.toLowerCase() === targetName.toLowerCase() ||
								   (tOrig && tOrig.toLowerCase() === targetName.toLowerCase());
						});
						if (targetNode) {
							break;
						}
					}
					
					// 判断相机类型并处理
					if (targetNode) {
						// 目标相机
						child.userData.targetPosition = targetNode.position.clone();
						child.userData.targetNode = targetNode;
						child.userData.cameraType = 'target';
						
						const lookAtResult = this.applyLookAt(child, child.userData.targetPosition, 'camera');
						child.userData.direction = lookAtResult.direction;
						
						// 计算并记录目标相机的roll角
						// 基于初始属性计算初始值
						// fbx没有提供quaternion轨道，fbxloader也无法读出curve
						// 目前无法复现fbx格式的roll
						// const rollResult = this.calculateCameraRollAngle(child);
						child.userData.rollAngle = 0;
						child.userData.upVector = new THREE.Vector3(0, 1, 0);
					} else {
						// 自由相机
						const rotationBefore = child.rotation.clone();
						
						// 检查是否已经应用过矫正
						if (!child.userData.appliedRotationCorrection) {
							// 检查是否有动画轨道
							let hasAnimationTracks = false;
							if (this.state.currentAnimations && this.state.currentAnimations.length > 0) {
								// 使用第一个动画剪辑检查
								const animationClip = this.state.currentAnimations[0];
								hasAnimationTracks = animationClip.tracks.some(track => track.name.startsWith(child.name + '.'));
							}
							
							if (hasAnimationTracks) {
								// 有动画轨道，根据格式决定是否设置矫正
								if (isFBX) {
									// FBX格式：设置fbxCorrectionQuaternion
									const correctionQuaternion = new THREE.Quaternion();
									correctionQuaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), -Math.PI/2);
									child.userData.fbxCorrectionQuaternion = correctionQuaternion.clone();
									child.userData.appliedRotationCorrection = true;
								}
								// GLB格式：不需要旋转矫正
							} else {
								// 无动画轨道，根据格式决定是否矫正
								if (isFBX) {
									// FBX格式：正常矫正
									this.applyRotationCorrection(child, 'camera');
								}
								// GLB格式：不需要旋转矫正
							}
						} else {
							// 已经应用过纠正
						}
						child.userData.cameraType = 'free';
						
						const rollResult = this.calculateCameraRollAngle(child);
						child.userData.rollAngle = rollResult.roll;
						child.userData.upVector = rollResult.upVector.clone();
					}
					
					// 检查并处理动画数据
					this.processCameraAnimationData(child);
					
					// 仅在正交相机时从相机属性初始化viewHeight
					if (child.isOrthographicCamera && !child.userData.viewHeight) {
						child.userData.viewHeight = child.top - child.bottom;
					}
					
					// 添加到场景相机列表
					this.state.cameras.scene.push(child);
					
					// 根据相机类型创建可视化箭头
					this.createCameraVisualization(child, 0x00ff00);
					
					child.visible = false;
				});
				
				if (this.state.cameras.scene.length > 0) {
					this.state.cameras.activeScene = this.state.cameras.scene[0];
				}
				
				// 为所有场景相机初始化状态存储
				this.state.cameras.scene.forEach(cam => {
					if (!this.state.cameras.states.has(cam.name)) {
						const viewHeight = cam.isOrthographicCamera ? (cam.userData.viewHeight || (cam.top - cam.bottom)) : null;
						this.state.cameras.states.set(cam.name, {
							position: cam.position.clone(),
							rotation: cam.rotation.clone(),
							fov: cam.fov,
							near: cam.near,
							far: cam.far,
							zoom: cam.zoom || 1,
							controlsTarget: this.controls.target.clone(),
							orthographic: cam.isOrthographicCamera,
							viewHeight: viewHeight,
							rollAngle: cam.userData.rollAngle || 0,
							upVector: cam.userData.upVector.clone()
						});
					}
				});
				
				this.updateViewsMenu();
				
				// 修复：确保所有关键帧中的position是Vector3对象
				this.fixAnimationKeyframeData(scene);
			}

			restoreExportedSceneCameras(scene) {
				// 清理旧场景相机的状态缓存
				this.state.cameras.scene.forEach(cam => {
					this.state.cameras.states.delete(cam.name);
				});
				
				this.state.cameras.scene.forEach(cam => {
					if (cam.userData.visualization) cam.userData.visualization.forEach(a => this.scene.remove(a));
					this.scene.remove(cam);
				});
				this.state.cameras.scene = [];
				this.state.cameras.activeScene = null;
				
				// 从场景的userData中获取导出的相机数据
				if (!scene.userData || !scene.userData.sceneCameras) {
					return;
				}
				
				const sceneCamerasData = scene.userData.sceneCameras;
				const targetNodesData = scene.userData.targetNodes || {};
				
				// 恢复目标节点
				const targetNodesMap = new Map();
				if (scene.userData.targetNodes) {
					// 先查找场景中已有的目标节点
					scene.traverse(child => {
						if (child.name && targetNodesData[child.name]) {
							targetNodesMap.set(child.name, child);
						}
					});
					
					// 对于数据中存在但场景中没有的节点，创建新的
					Object.keys(targetNodesData).forEach(nodeName => {
						if (!targetNodesMap.has(nodeName)) {
							const nodeData = targetNodesData[nodeName];
							const newNode = new THREE.Object3D();
							newNode.name = nodeName;
							
							if (nodeData.keyframes && nodeData.keyframes.length > 0) {
								newNode.userData.animationKeyframes = nodeData.keyframes.map(kfData => ({
									frame: kfData.frame,
									position: new THREE.Vector3().fromArray(kfData.position),
									rotation: kfData.rotation ? new THREE.Euler().fromArray(kfData.rotation) : new THREE.Euler()
								}));
							}
							
							newNode.userData.isTargetNode = true;
							newNode.userData.skipPreprocessing = true;
							
							scene.add(newNode);
							targetNodesMap.set(nodeName, newNode);
						}
					});
				}
				
				// 收集所有场景相机
				const sceneCameras = [];
				scene.traverse(child => {
					if (child.isCamera && child.name && sceneCamerasData[child.name]) {
						sceneCameras.push(child);
					}
				});
				
				// 恢复每个场景相机
				sceneCameras.forEach(child => {
					const cameraData = sceneCamerasData[child.name];
					
					// 确保userData存在
					if (!child.userData) child.userData = {};
					
					// 恢复动画关键帧（如果存在）
					if (cameraData.keyframes && cameraData.keyframes.length > 0) {
						child.userData.animationKeyframes = cameraData.keyframes.map(kfData => {
							const keyframe = {
								frame: kfData.frame,
								position: new THREE.Vector3().fromArray(kfData.position),
								rotation: new THREE.Euler().fromArray(kfData.rotation),
								fov: kfData.fov,
								roll: kfData.roll || 0,
								upVector: new THREE.Vector3().fromArray(kfData.upVector),
								cameraType: cameraData.cameraType || 'free'
							};
							
							// 恢复目标位置（如果是目标相机）
							if (kfData.targetPosition) {
								keyframe.targetPosition = new THREE.Vector3().fromArray(kfData.targetPosition);
							}
							
							// 恢复四元数（如果有）
							if (kfData.quaternion) {
								keyframe.quaternion = new THREE.Quaternion(
									kfData.quaternion[0],
									kfData.quaternion[1],
									kfData.quaternion[2],
									kfData.quaternion[3]
								);
							}
							
							return keyframe;
						});
					}
					
					// 恢复相机类型
					child.userData.cameraType = cameraData.cameraType || 'free';
					
					// 恢复目标节点关联
					if (cameraData.cameraType === 'target' && cameraData.targetNodeName) {
						const targetNode = targetNodesMap.get(cameraData.targetNodeName);
						if (targetNode) {
							child.userData.targetNode = targetNode;
							
							// 从关键帧中恢复targetPosition
							if (child.userData.animationKeyframes && child.userData.animationKeyframes.length > 0) {
								const firstKeyframe = child.userData.animationKeyframes[0];
								if (firstKeyframe.targetPosition) {
									child.userData.targetPosition = firstKeyframe.targetPosition.clone();
								}
							}
						}
					}
					
					// 恢复矫正信息
					if (cameraData.fbxCorrectionApplied) {
						child.userData.appliedRotationCorrection = true;
					}
					
					if (cameraData.fbxCorrectionQuaternion) {
						child.userData.fbxCorrectionQuaternion = new THREE.Quaternion(
							cameraData.fbxCorrectionQuaternion[0],
							cameraData.fbxCorrectionQuaternion[1],
							cameraData.fbxCorrectionQuaternion[2],
							cameraData.fbxCorrectionQuaternion[3]
						);
					}
					
					// 标记为已处理，跳过后续预处理
					child.userData.skipPreprocessing = true;
					child.userData.isSceneCamera = true;
					
					// 添加到场景相机列表
					this.state.cameras.scene.push(child);
					
					// 创建相机可视化
					this.createCameraVisualization(child, 0x00ff00);
					
					child.visible = false;
					
					// 初始化相机状态存储
					if (!this.state.cameras.states.has(child.name)) {
						const viewHeight = child.isOrthographicCamera ? 
							(child.userData.viewHeight || (child.top - child.bottom)) : null;
						
						this.state.cameras.states.set(child.name, {
							position: child.position.clone(),
							rotation: child.rotation.clone(),
							fov: child.fov,
							near: child.near,
							far: child.far,
							zoom: child.zoom || 1,
							controlsTarget: this.controls.target.clone(),
							orthographic: child.isOrthographicCamera,
							viewHeight: viewHeight,
							rollAngle: child.userData.rollAngle || 0,
							up: child.up.clone()
						});
					}
				});
				
				if (this.state.cameras.scene.length > 0) {
					this.state.cameras.activeScene = this.state.cameras.scene[0];
				}
				
				delete scene.userData.sceneCameras;
				delete scene.userData.targetNodes;
				delete scene.userData.customCameras;
				delete scene.userData.smplAnimation;
				
				// 清除子节点上的临时数据
				scene.traverse(child => {
					if (child.userData) {
						delete child.userData.sceneCameraData;
						delete child.userData.targetNodeData;
						delete child.userData.lightAnimationData;
						delete child.userData.customCameraData;
					}
				});
			}

			// 自定义相机关键帧
			addCameraKeyframe() {
				if (this.state.cameras.currentType !== 'custom') return;
				
				const frame = Math.floor(this.state.playback.currentFrame);
				
				let consistentTarget;
				
				// 确保control target不会出现在异常位置
				const currentDistance = this.camera.position.distanceTo(this.controls.target);
				
				if (currentDistance < this.state.controlTargetDist.minDist || currentDistance > this.state.controlTargetDist.maxDist) {
					const validDistance = Math.max(this.state.controlTargetDist.minDist, Math.min(this.state.controlTargetDist.maxDist, currentDistance));
					
					// 确保control target与相机方向一致
					const direction = new THREE.Vector3(0, 0, -1);
					direction.applyQuaternion(this.camera.quaternion);
					
					// 计算一致的control target
					consistentTarget = this.camera.position.clone().add(
						direction.multiplyScalar(validDistance)
					);
				} else {
					consistentTarget = this.controls.target.clone()
				}
				
				// 根据相机类型确定fov/viewHeight值
				let fovValue;
				if (this.camera.isOrthographicCamera) {
					// 正交相机：保存viewHeight
					fovValue = this.camera.userData.viewHeight || (this.camera.top - this.camera.bottom);
				} else {
					// 透视相机：保存fov
					fovValue = this.camera.fov;
				}
				
				const kf = { 
					frame, 
					position: this.camera.position.clone(), 
					rotation: this.camera.rotation.clone(), 
					fov: fovValue, 
					controlsTarget: consistentTarget.clone(), 
					roll: this.camera.userData.rollAngle || 0,
					upVector: this.camera.userData.upVector ? this.camera.userData.upVector.clone() : this.camera.up.clone(),
					sOrthographic: this.camera.isOrthographicCamera
				};
				
				// 确保关键帧数组存在
				if (!this.camera.userData.keyframes) {
					this.camera.userData.keyframes = [];
				}
				
				// 操作当前相机的动画轨
				const existingIndex = this.camera.userData.keyframes.findIndex(k => k.frame === frame);
				if (existingIndex >= 0) {
					this.camera.userData.keyframes[existingIndex] = kf;
				} else {
					this.camera.userData.keyframes.push(kf);
				}
				
				this.camera.userData.keyframes.sort((a,b) => a.frame - b.frame);
				this.state.cameraAnim.keyframes = [...this.camera.userData.keyframes];
				this.updateKeyframeCount();
				this.updateInfoDisplay();
				
				// 添加关键帧后，更新ortho切换状态
				this.updateOrthoToggleState();
			}

			deleteCurrentKeyframe() {
				// 只对自定义相机有效
				if (this.state.cameras.currentType !== 'custom') {
					return;
				}
				
				const frame = Math.floor(this.state.playback.currentFrame);
				const camera = this.camera;
				let deleted = false;
				
				// 从关键帧数组中删除
				if (camera.userData.keyframes) {
					const originalCount = camera.userData.keyframes.length;
					camera.userData.keyframes = camera.userData.keyframes.filter(k => k.frame !== frame);
					if (camera.userData.keyframes.length < originalCount) {
						deleted = true;
					}
				}
				
				// 删除后，更新ortho切换状态
				this.updateOrthoToggleState();
				
				// 从额外动画数据中删除（如果有）
				this.deleteFrameFromExtraAnimationData(camera, frame);
				
				// 更新状态中的关键帧
				this.state.cameraAnim.keyframes = [...(camera.userData.keyframes || [])];
				
				// 更新UI
				this.updateKeyframeCount();
				this.updateInfoDisplay();
			}

			clearCameraKeyframes() {
				// 只对自定义相机有效
				if (this.state.cameras.currentType !== 'custom') {
					return;
				}
				
				// 清除所有动画数据源
				const camera = this.camera;
				if (camera && camera.userData) {
					// 1. 清除关键帧数组
					camera.userData.keyframes = [];
					
					// 2. 清除额外的动画数据（FOV/Roll）
					delete camera.userData.animationFov;
					delete camera.userData.animationRoll;
					delete camera.userData.extraAnimationData;
					
					// 3. 清除序列化的关键帧数据（如果有）
					delete camera.userData.serializedKeyframes;
					
					// 4. 清除任何其他动画相关数据
					delete camera.userData.hasAnimation;
					delete camera.userData.animationClip;
					delete camera.userData.animationTracks;
				}
				
				// 清除后，更新ortho切换状态
				this.updateOrthoToggleState();
				
				// 清除状态中的动画数据
				this.state.cameraAnim.keyframes = [];
				
				// 重置相机的动画相关状态
				if (camera) {
					// 如果相机动画正在启用，恢复到编辑模式
					if (this.state.cameraAnim.isEnabled) {
						this.toggleCameraAnimation();
					}
					
					// 重置相机的动画混合器状态（如果有）
					if (camera.userData.animationMixer) {
						camera.userData.animationMixer.stopAllAction();
						delete camera.userData.animationMixer;
					}
					
					// 确保相机处于静止状态（使用当前位置和旋转）
					this.saveCurrentCameraState();
				}
				
				// 更新关键帧计数
				this.updateKeyframeCount();
				
				// 更新关键帧按钮状态
				this.updateKeyframeButtonsState();
				this.updateInfoDisplay();
			}

			deleteFrameFromExtraAnimationData(camera, frame) {
				if (!camera || !camera.userData) return;
				
				// 删除FOV动画中的该帧数据
				if (camera.userData.animationFov) {
					const fovData = camera.userData.animationFov;
					if (fovData.times && fovData.values) {
						this.deleteFrameFromAnimationData(fovData, frame, this.state.playback.fps);
					}
				}
				
				// 删除Roll动画中的该帧数据
				if (camera.userData.animationRoll) {
					const rollData = camera.userData.animationRoll;
					if (rollData.times && rollData.values) {
						this.deleteFrameFromAnimationData(rollData, frame, this.state.playback.fps);
					}
				}
				
				// 删除extraAnimationData中的该帧数据
				if (camera.userData.extraAnimationData) {
					const extraData = camera.userData.extraAnimationData;
					if (extraData.fov) {
						this.deleteFrameFromAnimationData(extraData.fov, frame, this.state.playback.fps);
					}
					if (extraData.roll) {
						this.deleteFrameFromAnimationData(extraData.roll, frame, this.state.playback.fps);
					}
				}
				
				// 删除序列化关键帧中的该帧数据
				if (camera.userData.serializedKeyframes) {
					const originalCount = camera.userData.serializedKeyframes.length;
					camera.userData.serializedKeyframes = camera.userData.serializedKeyframes.filter(k => k.frame !== frame);
					if (camera.userData.serializedKeyframes.length < originalCount) {
					}
				}
			}

			deleteFrameFromAnimationData(animationData, frame, fps) {
				// 将帧转换为时间
				const targetTime = frame / fps;
				
				// 查找最接近的时间索引
				let closestIndex = -1;
				let minDiff = Infinity;
				
				for (let i = 0; i < animationData.times.length; i++) {
					const diff = Math.abs(animationData.times[i] - targetTime);
					if (diff < minDiff && diff < 0.001) { // 允许微小误差
						minDiff = diff;
						closestIndex = i;
					}
				}
				
				// 删除该索引的数据
				if (closestIndex >= 0) {
					animationData.times.splice(closestIndex, 1);
					if (animationData.values.length > closestIndex) {
						// 根据数据类型删除相应数量的值
						if (Array.isArray(animationData.values)) {
							// 如果是数组，直接删除一个元素
							animationData.values.splice(closestIndex, 1);
						} else if (typeof animationData.values === 'object') {
							// 如果是对象，可能有不同的结构
							/* this.showMessage("Warning：animationData.values is an object, so frames cannot be deleted directly."); */
						}
					}
				}
			}

			//自定义相机导入
			identifyCustomCameras(scene) {
				const customCameras = [];
				
				scene.traverse(child => {
					// 检查是否为已导出的数据
					if (child.userData && child.userData.isExportedData) {
						// 如果是已导出的自定义相机，直接添加到自定义相机列表
						if (child.isCamera && child.name.startsWith("CustomCamJK_")) {
							customCameras.push(child);
							const num = parseInt(child.name.replace("CustomCamJK_", "")) || 0;
							this.state.cameras.customCount = Math.max(this.state.cameras.customCount, num);
							
							// 标记为已处理的自定义相机
							child.userData.skipPreprocessing = true;
							
							// 从场景相机数组中移除（如果存在的话）
							const sceneIndex = this.state.cameras.scene.indexOf(child);
							if (sceneIndex > -1) {
								this.state.cameras.scene.splice(sceneIndex, 1);
							}
						}
						return;
					}
					
					if (child.isCamera && child.name.startsWith("CustomCamJK_")) {
						// 记录自定义相机信息
						
						// 如果已经有关键帧数据，直接使用
						if (child.userData.keyframes && child.userData.keyframes.length > 0) {
							
							// 确保关键帧有所有必要属性
							child.userData.keyframes.forEach((kf, idx) => {
								if (!kf.hasOwnProperty('isOrthographic')) {
									kf.isOrthographic = child.isOrthographicCamera;
								}
								
								// 确保 controlsTarget 存在
								if (!kf.controlsTarget) {
									// 如果没有 controlsTarget，使用相机当前的 controlsTarget 或计算一个
									const direction = new THREE.Vector3(0, 0, -1);
									direction.applyQuaternion(new THREE.Quaternion().setFromEuler(kf.rotation));
									kf.controlsTarget = kf.position.clone().add(direction.multiplyScalar(5));
								}
							});
						}
						
						customCameras.push(child);
						const num = parseInt(child.name.replace("CustomCamJK_", "")) || 0;
						this.state.cameras.customCount = Math.max(this.state.cameras.customCount, num);
						
						// 从场景相机数组中移除（如果存在的话）
						const sceneIndex = this.state.cameras.scene.indexOf(child);
						if (sceneIndex > -1) {
							this.state.cameras.scene.splice(sceneIndex, 1);
						}
					}
				});
				
				customCameras.forEach(customCam => {
					// 检查是否已经存在于 custom 数组中
					const existingIndex = this.state.cameras.custom.findIndex(c => c.name === customCam.name);
					
					if (existingIndex === -1) {
						// 添加到自定义相机数组
						this.state.cameras.custom.push(customCam);
						
						// 创建可视化箭头
						this.createCameraVisualization(customCam, 0xffaa00);
					} else {
						// 如果已经存在，更新现有的相机
						this.state.cameras.custom[existingIndex] = customCam;
					}
					
					// 如果已经有关键帧数据，跳过动画轨道处理
					if (customCam.userData.keyframes && customCam.userData.keyframes.length > 0) {
						return;
					}
					
					// 否则，尝试从动画轨道提取关键帧
					if (this.state.currentAnimations && this.state.currentAnimations.length > 0) {
						const cameraAnimations = [];
						
						this.state.currentAnimations.forEach(clip => {
							const hasMatchingTrack = clip.tracks.some(track => {
								return track.name.startsWith(customCam.name + '.');
							});
							
							if (hasMatchingTrack) {
								cameraAnimations.push(clip);
							}
						});
						
						if (cameraAnimations.length > 0) {
							// 处理第一个匹配的动画剪辑
							this.processCustomCameraAnimationFromClip(customCam, cameraAnimations[0]);
						}
					}
				});
				
				// 更新视图菜单
				this.updateViewsMenu();
			}

			processCustomCameraAnimationFromClip(camera, animationClip) {
				if (!camera || !animationClip) return;
				
				const cameraName = camera.name;
				const fps = this.state.playback.fps;
				const duration = animationClip.duration;
				
				// 查找相机相关的轨道
				const cameraTracks = animationClip.tracks.filter(track => 
					track.name.startsWith(cameraName + ".")
				);
				
				if (cameraTracks.length === 0) {
					return;
				}
				
				// 初始化关键帧数组
				if (!camera.userData.keyframes) {
					camera.userData.keyframes = [];
				}
				
				// 从轨道中提取关键时间点
				const allKeyTimes = new Set();
				
				cameraTracks.forEach(track => {
					if (track.times) {
						track.times.forEach(time => allKeyTimes.add(time));
					}
				});
				
				// 将时间点转换为帧号并排序
				const keyFrames = Array.from(allKeyTimes)
					.map(time => Math.round(time * fps))
					.sort((a, b) => a - b);
				
				// 为每个关键时间点创建关键帧
				const newKeyframes = [];
				
				keyFrames.forEach((frame, index) => {
					const time = frame / fps;
					
					// 获取相机当前的基础属性
					const baseRoll = camera.userData.rollAngle || 0;
					const baseFov = camera.fov;
					const baseControlsTarget = camera.userData.controlsTarget || new THREE.Vector3(0, 1, 0);
					
					// 从现有关键帧中查找相同帧的数据，如果有的话
					const existingKeyframe = camera.userData.keyframes.find(k => k.frame === frame);
					
					// 创建关键帧
					const keyframe = {
						frame: frame,
						position: existingKeyframe ? existingKeyframe.position.clone() : camera.position.clone(),
						rotation: existingKeyframe ? existingKeyframe.rotation.clone() : camera.rotation.clone(),
						fov: existingKeyframe ? existingKeyframe.fov : baseFov,
						roll: existingKeyframe ? existingKeyframe.roll : baseRoll,
						controlsTarget: existingKeyframe ? existingKeyframe.controlsTarget.clone() : baseControlsTarget.clone(),
						isOrthographic: existingKeyframe ? 
							(existingKeyframe.isOrthographic !== undefined ? existingKeyframe.isOrthographic : camera.isOrthographicCamera) : 
							camera.isOrthographicCamera
					};
					
					newKeyframes.push(keyframe);
				});
				
				// 如果提取到了关键帧，合并到现有关键帧中
				if (newKeyframes.length > 0) {
					// 合并现有和新的关键帧
					const mergedKeyframes = [...camera.userData.keyframes];
					
					newKeyframes.forEach(newKf => {
						const existingIndex = mergedKeyframes.findIndex(k => k.frame === newKf.frame);
						if (existingIndex >= 0) {
							mergedKeyframes[existingIndex] = newKf;
						} else {
							mergedKeyframes.push(newKf);
						}
					});
					
					// 排序
					mergedKeyframes.sort((a, b) => a.frame - b.frame);
					camera.userData.keyframes = mergedKeyframes;
				}
			}

			createCustomCameraFromImported(importedCamera) {
				// 获取相机序号
				const cameraName = importedCamera.name;
				let cameraNumber = 0;
				
				if (cameraName.startsWith('CustomCamJK_')) {
					const numStr = cameraName.replace('CustomCamJK_', '');
					cameraNumber = parseInt(numStr) || 0;
				}
				
				// 更新自定义相机计数
				this.state.cameras.customCount = Math.max(this.state.cameras.customCount, cameraNumber);
				
				const container = this.dom.container;
				const aspect = container.clientWidth / container.clientHeight;
				
				// 根据导入相机的类型创建新相机
				let newCamera;
				
				if (importedCamera.isOrthographicCamera) {
					// 创建正交相机
					const viewHeight = importedCamera.userData && importedCamera.userData.viewHeight ? 
									  importedCamera.userData.viewHeight : 
									  (importedCamera.top - importedCamera.bottom) || 5;
					newCamera = new THREE.OrthographicCamera(
						-viewHeight * aspect / 2,
						viewHeight * aspect / 2,
						viewHeight / 2,
						-viewHeight / 2,
						importedCamera.near || 0.01,
						importedCamera.far || 500
					);
					newCamera.userData.viewHeight = viewHeight;
					newCamera.userData.initialViewHeight = viewHeight;
					newCamera.userData.actualZoomFactor = 1.0;
				} else {
					// 创建透视相机
					newCamera = new THREE.PerspectiveCamera(
						importedCamera.fov || 50,
						aspect,
						importedCamera.near || 0.01,
						importedCamera.far || 500
					);
				}
				
				newCamera.name = cameraName;
				
				// 应用从导入相机获取的当前帧状态
				newCamera.position.copy(importedCamera.position);
				newCamera.rotation.copy(importedCamera.rotation);
				
				// 获取关键属性，确保安全访问
				const importedUserData = importedCamera.userData || {};
				const importedCreationPose = importedUserData.creationPose || {};
				
				// 获取 controlsTarget
				let controlsTarget;
				if (importedCamera.userData && importedCamera.userData.controlsTarget) {
					controlsTarget = this.convertToVector3(importedCamera.userData.controlsTarget, new THREE.Vector3(0, 0, 0));
				} else if (importedCamera.userData && importedCamera.userData.creationPose && importedCamera.userData.creationPose.controlsTarget) {
					controlsTarget = this.convertToVector3(importedCamera.userData.creationPose.controlsTarget, new THREE.Vector3(0, 0, 0));
				} else {
					// 默认 controlsTarget：计算相机前方的点
					const direction = new THREE.Vector3(0, 0, -1);
					direction.applyQuaternion(newCamera.quaternion);
					controlsTarget = newCamera.position.clone().add(direction.multiplyScalar(this.state.controlTargetDist.defDist));
				}
				
				// 获取 rollAngle 和 upVector
				let rollAngle = 0;
				if (importedUserData.rollAngle !== undefined) {
					rollAngle = importedUserData.rollAngle;
				} else if (importedCreationPose.rollAngle !== undefined) {
					rollAngle = importedCreationPose.rollAngle;
				} else {
					// 如果没有保存的 rollAngle，则计算当前相机的 roll 角
					const rollResult = this.calculateCameraRollAngle(newCamera);
					rollAngle = rollResult.roll;
				}
				
				// 获取 upVector
				let upVector = new THREE.Vector3(0, 1, 0);
				if (importedUserData.upVector) {
					upVector = this.convertToVector3(importedUserData.upVector, new THREE.Vector3(0, 1, 0));
				} else if (importedCreationPose.upVector) {
					upVector = this.convertToVector3(importedCreationPose.upVector, new THREE.Vector3(0, 1, 0));
				} else {
					// 根据旋转计算 upVector
					upVector = new THREE.Vector3(0, 1, 0);
					upVector.applyQuaternion(newCamera.quaternion);
				}
				
				// 获取 initialDistance
				let initialDistance = 4;
				if (importedCreationPose.initialDistance !== undefined) {
					initialDistance = importedCreationPose.initialDistance;
				} else if (importedUserData.initialDistance !== undefined) {
					initialDistance = importedUserData.initialDistance;
				} else {
					// 计算相机到控制目标的距离
					initialDistance = newCamera.position.distanceTo(controlsTarget);
				}
				
				// 获取 viewHeight 相关属性
				const isOrthographic = importedCamera.isOrthographicCamera;
				let viewHeight = null;
				let initialViewHeight = null;
				
				if (isOrthographic) {
					viewHeight = importedUserData.viewHeight || 
								importedCreationPose.viewHeight || 
								(importedCamera.top - importedCamera.bottom) || 5;
					initialViewHeight = importedCreationPose.initialViewHeight || viewHeight;
				}
				
				// 获取 actualZoomFactor
				const actualZoomFactor = importedCreationPose.actualZoomFactor || importedUserData.actualZoomFactor || 1.0;
				
				// 获取 fixedView（如果是默认相机）
				const fixedView = importedUserData.fixedView || importedCreationPose.fixedView || false;
				const isDefault = importedUserData.isDefault || false;
				
				// 设置用户数据
				newCamera.userData = {
					...newCamera.userData,
					isDefault: isDefault,
					fixedView: fixedView,
					controlsTarget: controlsTarget.clone(),
					viewHeight: viewHeight,
					initialViewHeight: initialViewHeight,
					actualZoomFactor: actualZoomFactor,
					keyframes: [],
					rollAngle: rollAngle,
					upVector: upVector.clone(),
					initialDistance: initialDistance,
					creationPose: {
						position: newCamera.position.clone(),
						rotation: newCamera.rotation.clone(),
						fov: newCamera.fov,
						near: newCamera.near,
						far: newCamera.far,
						orthographic: isOrthographic,
						viewHeight: viewHeight,
						initialViewHeight: initialViewHeight,
						initialDistance: initialDistance,
						actualZoomFactor: actualZoomFactor,
						controlsTarget: controlsTarget.clone(),
						rollAngle: rollAngle,
						upVector: upVector.clone(),
						fixedView: fixedView
					}
				};
				
				// 应用 upVector 到相机
				newCamera.up.copy(upVector);
				
				// 保存相机状态到全局缓存
				this.state.cameras.states.set(cameraName, {
					position: newCamera.position.clone(),
					rotation: newCamera.rotation.clone(),
					fov: newCamera.fov,
					near: newCamera.near,
					far: newCamera.far,
					zoom: newCamera.zoom || 1,
					controlsTarget: controlsTarget.clone(),
					orthographic: isOrthographic,
					viewHeight: viewHeight,
					rollAngle: rollAngle,
					up: upVector.clone(),
					actualZoomFactor: actualZoomFactor
				});
				
				this.scene.add(newCamera);
				return newCamera;
			}

			// 动画关键帧修复
			fixAnimationKeyframeData(scene) {
				scene.traverse(child => {
					// 修复相机关键帧
					if (child.isCamera && child.userData.animationKeyframes) {
						child.userData.animationKeyframes = child.userData.animationKeyframes.map(kf => {
							// 修复position
							if (kf.position && !kf.position.isVector3) {
								if (Array.isArray(kf.position)) {
									kf.position = new THREE.Vector3(kf.position[0], kf.position[1], kf.position[2]);
								} else if (kf.position.x !== undefined) {
									kf.position = new THREE.Vector3(kf.position.x, kf.position.y, kf.position.z);
								}
							}
							
							// 修复rotation
							if (kf.rotation && !kf.rotation.isEuler) {
								if (Array.isArray(kf.rotation)) {
									kf.rotation = new THREE.Euler(kf.rotation[0], kf.rotation[1], kf.rotation[2]);
								} else if (kf.rotation.x !== undefined) {
									kf.rotation = new THREE.Euler(kf.rotation.x, kf.rotation.y, kf.rotation.z);
								}
							}
							
							return kf;
						});
					}
					
					// 修复目标节点关键帧
					if (child.userData && child.userData.animationKeyframes && child.userData.animationKeyframes.length > 0) {
						child.userData.animationKeyframes = child.userData.animationKeyframes.map(kf => {
							// 修复position
							if (kf.position && !kf.position.isVector3) {
								if (Array.isArray(kf.position)) {
									kf.position = new THREE.Vector3(kf.position[0], kf.position[1], kf.position[2]);
								} else if (kf.position.x !== undefined) {
									kf.position = new THREE.Vector3(kf.position.x, kf.position.y, kf.position.z);
								}
							}
							return kf;
						});
					}
					
					// 修复灯光关键帧
					if (child.isLight && child.userData.animationKeyframes) {
						child.userData.animationKeyframes = child.userData.animationKeyframes.map(kf => {
							// 修复position
							if (kf.position && !kf.position.isVector3) {
								if (Array.isArray(kf.position)) {
									kf.position = new THREE.Vector3(kf.position[0], kf.position[1], kf.position[2]);
								} else if (kf.position.x !== undefined) {
									kf.position = new THREE.Vector3(kf.position.x, kf.position.y, kf.position.z);
								}
							}
							
							// 修复rotation
							if (kf.rotation && !kf.rotation.isEuler) {
								if (Array.isArray(kf.rotation)) {
									kf.rotation = new THREE.Euler(kf.rotation[0], kf.rotation[1], kf.rotation[2]);
								} else if (kf.rotation.x !== undefined) {
									kf.rotation = new THREE.Euler(kf.rotation.x, kf.rotation.y, kf.rotation.z);
								}
							}
							
							// 修复targetPosition
							if (kf.targetPosition && !kf.targetPosition.isVector3) {
								if (Array.isArray(kf.targetPosition)) {
									kf.targetPosition = new THREE.Vector3(kf.targetPosition[0], kf.targetPosition[1], kf.targetPosition[2]);
								} else if (kf.targetPosition.x !== undefined) {
									kf.targetPosition = new THREE.Vector3(kf.targetPosition.x, kf.targetPosition.y, kf.targetPosition.z);
								}
							}
							
							return kf;
						});
					}
					
					// 修复自定义相机关键帧
					if (child.isCamera && child.userData.keyframes) {
						child.userData.keyframes = child.userData.keyframes.map(kf => {
							// 修复position
							if (kf.position && !kf.position.isVector3) {
								if (Array.isArray(kf.position)) {
									kf.position = new THREE.Vector3(kf.position[0], kf.position[1], kf.position[2]);
								} else if (kf.position.x !== undefined) {
									kf.position = new THREE.Vector3(kf.position.x, kf.position.y, kf.position.z);
								}
							}
							
							// 修复rotation
							if (kf.rotation && !kf.rotation.isEuler) {
								if (Array.isArray(kf.rotation)) {
									kf.rotation = new THREE.Euler(kf.rotation[0], kf.rotation[1], kf.rotation[2]);
								} else if (kf.rotation.x !== undefined) {
									kf.rotation = new THREE.Euler(kf.rotation.x, kf.rotation.y, kf.rotation.z);
								}
							}
							
							// 修复controlsTarget
							if (kf.controlsTarget && !kf.controlsTarget.isVector3) {
								if (Array.isArray(kf.controlsTarget)) {
									kf.controlsTarget = new THREE.Vector3(kf.controlsTarget[0], kf.controlsTarget[1], kf.controlsTarget[2]);
								} else if (kf.controlsTarget.x !== undefined) {
									kf.controlsTarget = new THREE.Vector3(kf.controlsTarget.x, kf.controlsTarget.y, kf.controlsTarget.z);
								}
							}
							
							return kf;
						});
					}
				});
			}

			// SMPL可见性动画
			processSMPLVisibilityAnimation(scene) {
				// 检查场景中是否有SMPL可见性数据
				if (!scene.userData || !scene.userData.smplAnimation || !scene.userData.smplAnimation.visibility) {
					return;
				}
				
				const smplData = scene.userData.smplAnimation.visibility;
				
				// 收集所有SMPL网格并按帧索引组织
				const smplFrames = [];
				const allSmplMeshes = [];
				
				// 首先，遍历场景找到所有SMPL帧网格
				const frameMeshes = [];
				scene.traverse(child => {
					if (child.isMesh && child.userData && child.userData.isSMPLFrame) {
						const frameIndex = child.userData.frameIndex || 0;
						frameMeshes.push({
							mesh: child,
							frameIndex: frameIndex
						});
					}
				});
				
				// 按帧索引排序
				frameMeshes.sort((a, b) => a.frameIndex - b.frameIndex);
				
				// 构建smplFrames数组
				for (const {mesh, frameIndex} of frameMeshes) {
					// 确保数组有足够的长度
					while (smplFrames.length <= frameIndex) {
						smplFrames.push([]);
					}
					
					// 将网格添加到对应帧的数组
					smplFrames[frameIndex].push(mesh);
					allSmplMeshes.push(mesh);
					
					// 重要：不在这里设置可见性，由updateVisuals统一管理
					// 但我们需要根据smplData中的初始可见性设置
					const visibilityKeyframe = smplData.visibilityKeyframes.find(kf => kf.frame === frameIndex);
					if (visibilityKeyframe) {
						mesh.visible = visibilityKeyframe.visible;
					} else {
						// 如果没有可见性数据，根据原始逻辑设置
						// frame < 1显示第1帧
						mesh.visible = (frameIndex === 1);
					}
				}
				
				// 更新状态中的SMPL数据
				if (allSmplMeshes.length > 0) {
					this.state.smplData = {
						numFrames: smplFrames.length,
						smplFrames: smplFrames,
						allMeshes: allSmplMeshes,
						visibilityData: smplData
					};
					
					// 确保播放器总帧数正确
					this.state.playback.totalFrames = smplFrames.length;
					
					// 根据原始逻辑，初始状态下如果当前帧<1，应该显示第1帧
					const currentFrame = Math.floor(this.state.playback.currentFrame);
					this.updateSMPLVisibility(currentFrame);
				}
			}

			updateSMPLVisibility(frame) {
				if (!this.state.smplData || !this.state.smplData.smplFrames) {
					return;
				}
				
				const smplFrames = this.state.smplData.smplFrames;
				const frameIndex = Math.floor(frame);
				
				// 计算要显示的实际帧索引 - 遵循原始逻辑
				let visibleFrame;
				if (smplFrames.length === 0) {
					visibleFrame = 1;
				} else if (frameIndex < 1) {
					// 小于1时显示第1帧
					visibleFrame = 1;
				} else if (frameIndex >= smplFrames.length) {
					// 大于等于长度时显示最后一帧
					visibleFrame = smplFrames.length - 1;
				} else {
					visibleFrame = frameIndex;
				}
				
				// 确保displayFrame在有效范围内
				visibleFrame = Math.max(1, Math.min(visibleFrame, smplFrames.length - 1));
				
				// 遍历所有帧，设置可见性
				let visibleCount = 0;
				let totalCount = 0;
				
				for (let i = 0; i < smplFrames.length; i++) {
					const meshes = smplFrames[i];
					if (meshes && meshes.length > 0) {
						totalCount += meshes.length;
						const isVisible = (i === visibleFrame);
						if (isVisible) {
							visibleCount += meshes.length;
						}
					  
						meshes.forEach(mesh => {
							mesh.visible = isVisible;
						});
					}
				}
			}

			// 可视化
			createCameraVisualization(camera, color) {
				// 确保userData存在
				if (!camera.userData) camera.userData = {};
				
				const baseLength = 1.25;
				const baseHeadLength = 0.25;
				const baseHeadWidth = 0.125;
				
				const length = baseLength * this.state.helperSize;
				const headLength = baseHeadLength * this.state.helperSize;
				const headWidth = baseHeadWidth * this.state.helperSize;
				
				const arrowHelper = new THREE.ArrowHelper(
					new THREE.Vector3(),
					camera.position,
					length,
					color,
					headLength,
					headWidth
				);
				
				// 保存原始尺寸以便后续缩放
				arrowHelper.userData.originalLength = baseLength;
				arrowHelper.userData.originalHeadLength = baseHeadLength;
				arrowHelper.userData.originalHeadWidth = baseHeadWidth;
				
				if (camera.userData.cameraType === 'target') {
					// 目标相机：箭头指向目标点
					let direction;
					if (camera.userData.targetPosition) {
						direction = new THREE.Vector3();
						direction.subVectors(camera.userData.targetPosition, camera.position);
						direction.normalize();
					} else {
						// 如果没有目标点，根据相机方向计算前方点
						direction = new THREE.Vector3(0, 0, -1);
						direction.applyQuaternion(camera.quaternion);
					}
					arrowHelper.setDirection(direction)
					arrowHelper.userData.isTargetCameraArrow = true;
				} else {
					// 自由相机：根据相机方向计算前方点
					const direction = new THREE.Vector3(0, 0, -1);
					direction.applyQuaternion(camera.quaternion);
					arrowHelper.setDirection(direction)
					arrowHelper.userData.isFreeCameraArrow = true;
				}
				
				if (!camera.userData.visualization) camera.userData.visualization = [];
				camera.userData.visualization.push(arrowHelper);
				
				// 保存相机引用，以便更新时使用
				arrowHelper.userData.camera = camera;
				
				this.scene.add(arrowHelper);
				return arrowHelper;
			}

			createLightVisualization(light, targetNodes = []) {
				// 确保userData存在
				if (!light.userData) light.userData = {};
				
				// 跳过环境光，不需要可视化
				if (light.type === 'AmbientLight') {
					return;
				}
				
				// 如果已经有可视化，先清理
				if (light.userData.sphereVisualization) {
					this.scene.remove(light.userData.sphereVisualization);
					if (light.userData.sphereVisualization.geometry) {
						light.userData.sphereVisualization.geometry.dispose();
					}
					if (light.userData.sphereVisualization.material) {
						light.userData.sphereVisualization.material.dispose();
					}
					light.userData.sphereVisualization = null;
				}
				
				const color = 0xffff00; // 黄色表示灯光
				
				// 使用球体表示所有灯光
				const baseRadius = 0.125;
				const radius = baseRadius * this.state.helperSize;
				const sphereGeometry = new THREE.SphereGeometry(radius, 4, 2);
				
				const sphereMaterial = new THREE.MeshBasicMaterial({ 
					color: color, 
					wireframe: true,
					transparent: true,
					opacity: 0.7
				});
				
				const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
				sphere.position.copy(light.position);
				light.userData.sphereVisualization = sphere;
				
				// 保存原始尺寸以便后续缩放
				light.userData.originalSphereRadius = baseRadius;
				
				// 标记可视化类型
				sphere.userData.isLightSphere = true;
				sphere.userData.lightType = light.type;
				sphere.userData.lightName = light.name;
				
				this.scene.add(sphere);
				
				// 初始可见性
				sphere.visible = false;
			}

			updateVisualizationVisibility() {
				const isGrid = this.dom.toggles.helper.checked;
				const useSceneLight = this.state.useSceneLight;
				
				// 更新相机可视化
				let currentActiveCamera = null;
				const activeName = this.dom.inputs.views.value;
				currentActiveCamera = this.state.cameras.default.find(c => c.name === activeName) || 
									this.state.cameras.custom.find(c => c.name === activeName) || 
									this.state.cameras.scene.find(c => c.name === activeName);
				
				this.state.cameras.custom.forEach(cam => {
					if (cam.userData.visualization) cam.userData.visualization.forEach(arrow => {
						arrow.visible = (cam !== currentActiveCamera) && isGrid;
					}); 
				});
				
				this.state.cameras.scene.forEach(cam => {
					if (cam.userData.visualization) cam.userData.visualization.forEach(arrow => {
						arrow.visible = (cam !== currentActiveCamera) && isGrid;
					});
				});
				
				// 场景灯光：仅在启用场景灯光且显示helper时可见
				this.state.lights.scene.forEach(light => {
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.visible = useSceneLight && isGrid;
					}
					// 清理旧的箭头可视化（如果有）
					if (light.userData.visualization) {
						light.userData.visualization.forEach(arrow => {
							arrow.visible = false;
						});
					}
				});
				
				// 默认灯光：仅在启用默认灯光且显示helper时可见
				this.state.lights.default.forEach(light => {
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.visible = !useSceneLight && isGrid;
					}
					// 清理旧的箭头可视化（如果有）
					if (light.userData.visualization) {
						light.userData.visualization.forEach(arrow => {
							arrow.visible = false;
						});
					}
				});
			}

			updateVisualizationPoses() {
				// 更新场景相机箭头
				this.state.cameras.scene.forEach(camera => {
					if (camera.userData.visualization) {
						camera.userData.visualization.forEach(arrow => {
							if (!arrow || !arrow.position) return;
							
							if (arrow.userData && arrow.userData.isTargetCameraArrow) {
								// 目标相机箭头：位置跟随相机，方向指向目标点
								arrow.position.copy(camera.position);
								
								let direction;
								if (camera.userData.targetPosition) {
									direction = new THREE.Vector3();
									direction.subVectors(camera.userData.targetPosition, camera.position);
									direction.normalize();
									arrow.setDirection(direction);
								} else {
									// 自由相机箭头：根据相机方向计算前方点
									direction = new THREE.Vector3(0, 0, -1);
									direction.applyQuaternion(camera.quaternion);
									arrow.setDirection(direction.normalize());
								}
							} else if (arrow.userData && arrow.userData.isFreeCameraArrow) {
								// 自由相机箭头：位置跟随相机，方向与相机一致
								arrow.position.copy(camera.position);
								// 根据相机方向计算前方点
								const direction = new THREE.Vector3(0, 0, -1);
								direction.applyQuaternion(camera.quaternion);
								arrow.setDirection(direction.normalize());
							}
						});
					}
				});
				
				// 更新自定义相机箭头
				this.state.cameras.custom.forEach(camera => {
					if (camera.userData.visualization) {
						camera.userData.visualization.forEach(arrow => {
							if (!arrow || !arrow.position) return;
							
							// 直接使用相机当前位置和旋转（已在updateCustomCameraPose中更新）
							arrow.position.copy(camera.position);
							
							// 根据相机方向计算前方点
							const direction = new THREE.Vector3(0, 0, -1);
							direction.applyQuaternion(camera.quaternion);
							arrow.setDirection(direction.normalize());
						});
					}
				});
				
				// 场景灯光
				this.state.lights.scene.forEach(light => {
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.position.copy(light.position);
					}
				});
				
				// 默认灯光
				this.state.lights.default.forEach(light => {
					if (light.userData.sphereVisualization) {
						light.userData.sphereVisualization.position.copy(light.position);
					}
				});
			}

			updateAllVisualizationSizes() {
				const scale = this.state.helperSize;
				
				this.state.cameras.custom.forEach(camera => {
					if (camera.userData.visualization) {
						camera.userData.visualization.forEach(arrow => {
							if (arrow && arrow.userData && arrow.userData.originalLength !== undefined) {
								arrow.setLength(arrow.userData.originalLength * scale);
							}
						});
					}
				});
				
				this.state.cameras.scene.forEach(camera => {
					if (camera.userData.visualization) {
						camera.userData.visualization.forEach(arrow => {
							if (arrow && arrow.userData && arrow.userData.originalLength !== undefined) {
								arrow.setLength(arrow.userData.originalLength * scale);
							}
						});
					}
				});
				
				const updateLightSphere = (light) => {
					if (light.userData.sphereVisualization && light.userData.originalSphereRadius !== undefined) {
						const sphere = light.userData.sphereVisualization;
						const newRadius = light.userData.originalSphereRadius * scale;
						
						const sphereGeometry = new THREE.SphereGeometry(newRadius, 4, 2);
						sphere.geometry.dispose();
						sphere.geometry = sphereGeometry;
					}
				};
				
				this.state.lights.scene.forEach(updateLightSphere);
				this.state.lights.default.forEach(updateLightSphere);
			}

        }

        const viewer = new Adv3DViewer();
    </script>
</body>
</html>`

app.registerExtension({
    name: "Comfy.JakeUpgrade.Adv3DViewer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Adv3DViewer_JK") {
            var onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                var r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
				// 创建容器
				var container = document.createElement("div");
                container.style.width = "100%";
				container.style.height = "100%";
				container.style.background = "#222";
				container.style.display = "flex";
				container.style.flexDirection = "column";
                
				// 创建iframe
				var iframe = document.createElement("iframe");
                iframe.style.width = "100%";
				iframe.style.height = "100%";
				iframe.style.border = "none";
				iframe.style.flexGrow = "1";
				iframe.srcdoc = ADV3DVIEWER_HTML;
                container.appendChild(iframe);
				
                // 添加最小尺寸样式
                var style = document.createElement('style');
                style.textContent = `
                    .node[data-id="${this.id}"] {
                        min-width: 420px !important;
                        min-height: 710px !important;
                        width: 980px !important;
                        height: 710px !important;
                    }
                `;
				document.head.appendChild(style);
                
				var widget = this.addDOMWidget("universal_viewer", "iframe", container, { serialize: false });
                
				// 设置初始尺寸
				this.setSize([980, 710]);
				
				// 存储最小尺寸
                this._minSize = [420, 710];
				
                // 添加最小尺寸限制
                var originalSetSize = this.setSize;
                this.setSize = function(size) {
                    var width = Math.max(size[0], this._minSize[0]);
                    var height = Math.max(size[1], this._minSize[1]);
                    return originalSetSize.call(this, [width, height]);
                };
				
                var resizeObserver = new ResizeObserver(function(entries) {
					for (var i = 0; i < entries.length; i++) {}
				});
                resizeObserver.observe(container);
				
                this.onExecuted = function(msg) {
                    if (msg && msg.file_path) {
                        var filename = msg.file_path[0];
						var format = msg.format ? msg.format[0] : 'auto';
                        var send = function() {
							iframe.contentWindow.postMessage({
								type: 'loadData',
								filename: filename,
								format: format
							}, '*');
						};
                        if (!iframe.contentDocument || iframe.contentDocument.readyState !== 'complete')
							iframe.onload = send;
						else
							send();
                    }
                };
				
                this.onRemoved = function() {
					resizeObserver.disconnect();
					
                    // 移除添加的样式
                    if (style.parentNode) {
                        style.parentNode.removeChild(style);
                    }
				};
                return r;
            };
        }
    }
});
