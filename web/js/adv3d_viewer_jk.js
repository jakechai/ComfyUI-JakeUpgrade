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
		
		/* 导入界面*/
		#loading {
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			color: white;
			font-size: 14px;
			background: rgba(0, 0, 0, 0.9);
			padding: 20px 30px;
			border-radius: 10px;
			border: 2px solid rgba(74, 158, 255, 0.5);
			z-index: 100;
			display: none;
			min-width: 200px;
			text-align: center;
			backdrop-filter: blur(10px);
			box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
		}
		.loading-progress {
			width: 100%;
			height: 4px;
			background: rgba(255, 255, 255, 0.1);
			border-radius: 2px;
			margin-top: 10px;
			overflow: hidden;
			position: relative;
		}
		.loading-progress-bar {
			width: 0%;
			height: 100%;
			background: linear-gradient(90deg, var(--primary-color), #3a8eef);
			border-radius: 2px;
			transition: width 0.3s ease;
		}
		.loading-spinner {
			width: 40px;
			height: 40px;
			border: 3px solid rgba(255, 255, 255, 0.1);
			border-top: 3px solid var(--primary-color);
			border-radius: 50%;
			animation: loadingSpin 1s linear infinite;
			margin: 0 auto 15px auto;
			display: none;
		}
		.loading-percentage {
			font-family: monospace;
			font-size: 12px;
			color: var(--primary-color);
			margin-top: 5px;
			display: none;
		}
		
		.disabled-control {
			opacity: 0.4 !important;
			cursor: not-allowed !important;
			pointer-events: none !important;
			user-select: none !important;
			position: relative;
		}
		
		.controls-disabled::after {
			content: '';
			position: absolute;
			top: 0;
			left: 0;
			right: 0;
			bottom: 0;
			background: rgba(0, 0, 0, 0.2);
			z-index: 100;
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
		.time-slider { width: 214px; }
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
			width: 70px;
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
			width: 54px;
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
		
		/* 灯光GUI容器样式 */
		.light-gui-container {
			position: absolute;
			top: 8px;
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
		
		/* 材质GUI容器样式 */
		.material-gui-container {
			position: absolute;
			top: 30px;
			right: 8px;
			z-index: 1000;
			background: rgba(30, 30, 30, 0.9);
			border: 1px solid #444;
			border-radius: 3px;
			padding: 4px;
			width: 180px;
			max-height: 502px;
			overflow-y: auto;
			backdrop-filter: blur(5px);
		}
		
		.light-gui-disabled, .material-gui-disabled, .selected-material-gui-disabled {
			display: none !important;
		}
		
		/* 文件夹及按键文本不溢出 */
		.lil-gui .controller {
			max-width: 100%;
			overflow: hidden;
		}
		.lil-gui .controller .property-name {
			white-space: nowrap;
			overflow: hidden;
			text-overflow: ellipsis;
		}
		.lil-gui button {
			white-space: nowrap;
			overflow: hidden;
			text-overflow: ellipsis;
			max-width: 100%;
		}
		.lil-gui .folder {
			margin-left: 8px;
		}
		
		/* 动画*/
		@keyframes pulse {
			0% { background-color: #ff4444; }
			50% { background-color: #ff8888; }
			100% { background-color: #ff4444; }
		}
		@keyframes loadingPulse {
			0% { 
				background-color: rgba(0, 0, 0, 0.9);
				box-shadow: 0 0 5px rgba(74, 158, 255, 0.5);
			}
			50% { 
				background-color: rgba(30, 30, 30, 0.95);
				box-shadow: 0 0 15px rgba(74, 158, 255, 0.8);
			}
			100% { 
				background-color: rgba(0, 0, 0, 0.9);
				box-shadow: 0 0 5px rgba(74, 158, 255, 0.5);
			}
		}
		@keyframes loadingSpin {
			0% { transform: translate(-50%, -50%) rotate(0deg); }
			100% { transform: translate(-50%, -50%) rotate(360deg); }
		}
		
	</style>
</head>
<body>
    <div id="container">
        <div id="canvas-container">
			<div id="loading">
				<div class="loading-spinner" id="loading-spinner"></div>
				<div id="loading-text">Waiting for 3D data...</div>
				<div class="loading-progress">
					<div class="loading-progress-bar" id="loading-progress-bar"></div>
				</div>
				<div class="loading-percentage" id="loading-percentage">0%</div>
			</div>
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
                    <button id="focus-light" class="compact-btn" title="Focus Default Directional Light to Scene">💢</button>
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
					<button id="screenshot-btn" title="Screenshot">🖨️</button>
					<button id="record-btn" class="file-btn record-btn" title="Record Video">🎬</button>
					<button id="threed-data-btn" class="file-btn threed-data-btn" title="Get Scene 3D Data">📦</button>
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
					<button id="center-to-object-btn" title="Move Camera to Object Center">👁️</button>
					<button id="focus-to-object-btn" title="Set Near and Far Clip Plane to Object Depth">📐</button>
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
	
    <input type="file" id="import-file-input" class="hidden-file-input" accept=".glb,.gltf,.fbx,.bin,.obj,.ply,.zip">
	
    <script type="importmap">
    {
        "imports": {
            "three": "https://cdn.jsdelivr.net/npm/three@0.162.0/build/three.module.js",
			"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.162.0/examples/jsm/",
			"jszip": "https://esm.sh/jszip@3.10.1"
        }
    }
    </script>
	
    <script type="module">
		import * as THREE from 'three';
		import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
		import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
		import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
		import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
		import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
		import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
		import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';
		import { TextureLoader } from 'three';
		import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
		import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
		import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
		import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
		import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
		import * as fflate from 'three/addons/libs/fflate.module.js';
		import JSZip from 'jszip';

		// 路径工具
		class PathUtils {
			// 通用清理路径
			static cleanTextureUrl(url) {
				if (!url) return '';
				
				// 移除Windows盘符
				let cleaned = url.replace(/^[a-zA-Z]:[\\\\/]/, '');
				
				// 统一路径分隔符
				cleaned = cleaned.replace(/\\\\/g, '/');
				
				// 移除前导斜杠
				if (cleaned.startsWith('/')) {
					cleaned = cleaned.substring(1);
				}
				
				// 提取文件名（只保留最后一部分）
				const parts = cleaned.split('/');
				let fileName = parts[parts.length - 1];
				
				// 处理可能包含查询参数或片段的情况
				fileName = fileName.split('?')[0].split('#')[0];
				
				return fileName;
			}

			static cleanTextureUrlSimple(url) {
				if (!url) return '';
				
				// 提取文件名（只保留最后一部分）
				const parts = url.split(/[\\\\/]/);
				let fileName = parts[parts.length - 1];
				
				// 处理可能包含查询参数或片段的情况
				fileName = fileName.split('?')[0].split('#')[0];
				
				return fileName;
			}

			// 清理zip虚拟环境路径
			static cleanPath(path) {
				if (!path) return '';
				
				// 移除Windows盘符
				let cleaned = path.replace(/^[a-zA-Z]:[\\\\/]/, '');
				
				// 统一路径分隔符
				cleaned = cleaned.replace(/\\\\/g, '/');
				
				// 移除前导斜杠
				if (cleaned.startsWith('/')) {
					cleaned = cleaned.substring(1);
				}
				
				// 解析相对路径（简化版）
				const parts = cleaned.split('/');
				const result = [];
				
				for (const part of parts) {
					if (part === '..') {
						if (result.length > 0) {
							result.pop();
						}
					} else if (part !== '.' && part !== '') {
						result.push(part);
					}
				}
				
				return result.join('/');
			}

			// 清理纹理路径（MTL解析器专用）
			static cleanTexturePath(path) {
				if (!path) return '';
				
				// 移除引号
				let cleaned = path.replace(/["']/g, '');
				
				// 移除尾部空格
				cleaned = cleaned.trim();
				
				// 统一路径分隔符
				cleaned = cleaned.replace(/\\\\/g, '/');
				
				return cleaned;
			}

			// 从文件路径中提取文件名
			static getFileName(filePath) {
				if (!filePath) return '';
				
				// 处理各种路径格式
				const path = filePath.replace(/\\\\/g, '/');
				const parts = path.split('/');
				return parts[parts.length - 1];
			}

			// 连接两个路径
			static joinPaths(base, relative) {
				if (!base) return relative;
				if (!relative) return base;
				
				const baseParts = base.split('/').filter(p => p !== '');
				const relativeParts = relative.split('/').filter(p => p !== '');
				
				for (const part of relativeParts) {
					if (part === '..') {
						if (baseParts.length > 0) {
							baseParts.pop();
						}
					} else if (part !== '.') {
						baseParts.push(part);
					}
				}
				
				return baseParts.join('/');
			}

			// 获取相对于主文件的路径
			static getRelativePath(mainFilePath, texturePath) {
				if (!mainFilePath || !texturePath) return texturePath;
				
				const mainDir = mainFilePath.substring(0, mainFilePath.lastIndexOf('/') + 1);
				return mainDir + texturePath;
			}

			// 解析路径的各个部分
			static parsePath(filePath) {
				if (!filePath) return { dir: '', name: '', ext: '', fullName: '' };
				
				const cleanedPath = filePath.replace(/\\\\/g, '/');
				const lastSlashIndex = cleanedPath.lastIndexOf('/');
				
				const dir = lastSlashIndex >= 0 ? cleanedPath.substring(0, lastSlashIndex + 1) : '';
				const fullName = lastSlashIndex >= 0 ? cleanedPath.substring(lastSlashIndex + 1) : cleanedPath;
				
				const lastDotIndex = fullName.lastIndexOf('.');
				const name = lastDotIndex >= 0 ? fullName.substring(0, lastDotIndex) : fullName;
				const ext = lastDotIndex >= 0 ? fullName.substring(lastDotIndex + 1).toLowerCase() : '';
				
				return {
					dir,
					name,
					ext,
					fullName,
					fullPath: cleanedPath
				};
			}
		}

		// 载入提示管理
		class LoadingProgressManager {
			constructor(viewer) {
				this.viewer = viewer;
				this.progress = 0;
				this.message = "";
				this.interval = null;
				this.step = 0;
				this.totalSteps = 10;
				this.startTime = null;
			}

			start(message = "Loading...", startProgress = 95) {
				this.progress = startProgress;
				this.message = message;
				this.step = 0;
				this.startTime = Date.now();
				
				// 清除之前的进度间隔
				this.stop();
				
				if (this.viewer && this.viewer.dom && this.viewer.dom.loading) {
					this.viewer.dom.loading.style.display = 'block';
				}
				
				this.viewer.updateLoadingProgress(this.progress, this.message);
				
				// 设置进度更新间隔
				this.interval = setInterval(() => {
					this.step++;
					if (this.step <= this.totalSteps) {
						const elapsed = Date.now() - this.startTime;
						// 根据时间动态调整进度速度
						const timeFactor = Math.min(1, elapsed / 5000);
						const incrementalProgress = startProgress + (timeFactor * (98 - startProgress) * (this.step / this.totalSteps));
						
						this.progress = Math.min(98, incrementalProgress);
						this.viewer.updateLoadingProgress(this.progress, this.message);
					} else {
						this.stop();
					}
				}, 300);
			}

			update(message, progress = null) {
				if (progress !== null) {
					this.progress = progress;
				}
				if (message) {
					this.message = message;
				}
				this.viewer.updateLoadingProgress(this.progress, this.message);
			}

			stop(finalMessage = "Processing complete") {
				if (this.interval) {
					clearInterval(this.interval);
					this.interval = null;
				}
				this.viewer.updateLoadingProgress(99, finalMessage);
				
				// 短暂延迟后显示100%
				setTimeout(() => {
					this.viewer.updateLoadingProgress(100, "Load complete");
				}, 300);
			}

			error(errorMessage) {
				this.stop();
				this.viewer.updateLoadingProgress(100, errorMessage);
			}
		}

		// 贴图管理
		class TextureManager {
			constructor(viewer) {
				this.viewer = viewer;
				this.textureLoader = new THREE.TextureLoader();
			}

			async loadTexture(material, propertyName, isColorMap = false) {
				return new Promise((resolve, reject) => {
					try {
						const input = document.createElement('input');
						input.type = 'file';
						input.accept = 'image/*';
						input.style.display = 'none';
						
						const cleanup = () => {
							if (document.body.contains(input)) {
								document.body.removeChild(input);
							}
						};
						
						input.onchange = async (e) => {
							const file = e.target.files[0];
							if (!file) {
								cleanup();
								reject(new Error('No file selected'));
								return;
							}
							
							try {
								const reader = new FileReader();
								
								reader.onload = (event) => {
									const image = new Image();
									
									image.onload = () => {
										const texture = new THREE.Texture(image);
										
										// 关键设置：立即更新纹理
										texture.needsUpdate = true;
										
										// 设置编码
										texture.encoding = isColorMap ? 
											THREE.sRGBEncoding : 
											THREE.LinearEncoding;
										
										// 保存文件名到userData
										texture.userData = texture.userData || {};
										texture.userData.filename = file.name;
										
										// 应用到材质
										material[propertyName] = texture;  // 重要：立即应用到材质
										
										// 保存到缓存
										if (!material._textureCache) {
											material._textureCache = {};
										}
										material._textureCache[propertyName] = texture;
										
										// 设置默认参数
										this.setDefaultTextureParameters(material, propertyName);
										
										// 强制材质更新
										material.needsUpdate = true;
										
										cleanup();
										resolve(texture);
									};
									
									image.onerror = () => {
										cleanup();
										reject(new Error('Failed to load image'));
									};
									
									image.src = event.target.result;
								};
								
								reader.onerror = () => {
									cleanup();
									reject(new Error('Failed to read file'));
								};
								
								reader.readAsDataURL(file);
							} catch (error) {
								cleanup();
								reject(error);
							}
						};
						
						// 添加取消处理
						input.oncancel = () => {
							cleanup();
							reject(new Error('File selection cancelled'));
						};
						
						// 添加到DOM并触发点击
						document.body.appendChild(input);
						input.click();
						
					} catch (error) {
						reject(error);
					}
				});
			}

			toggleTexture(material, propertyName, enabled) {
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				if (enabled) {
					// 从缓存中恢复贴图（需要确保缓存中有贴图）
					if (material._textureCache[propertyName]) {
						material[propertyName] = material._textureCache[propertyName];
						// 确保纹理已更新
						if (material[propertyName]) {
							material[propertyName].needsUpdate = true;
						}
					} else {
						// 如果没有贴图文件，保持null
						material[propertyName] = null;
					}
				} else {
					// 禁用贴图，但保留在缓存中（不删除贴图文件）
					material[propertyName] = null;
				}
				
				material.needsUpdate = true;
			}

			removeTexture(material, propertyName) {
				// 从材质中移除贴图应用
				const texture = material[propertyName];
				material[propertyName] = null;
				
				// 从缓存中移除贴图
				if (material._textureCache && material._textureCache[propertyName]) {
					// 释放纹理资源
					const cachedTexture = material._textureCache[propertyName];
					if (cachedTexture.dispose) {
						cachedTexture.dispose();
					}
					delete material._textureCache[propertyName];
				}
				
				// 重置相关参数
				this.resetTextureParameters(material, propertyName);
				
				material.needsUpdate = true;
			}

			setDefaultTextureParameters(material, propertyName) {
				switch (propertyName) {
					case 'normalMap':
						if (!material.normalScale) {
							material.normalScale = new THREE.Vector2(1, 1);
						}
						break;
					case 'bumpMap':
						if (material.bumpScale === undefined) {
							material.bumpScale = 1;
						}
						break;
					case 'aoMap':
						if (material.aoMapIntensity === undefined) {
							material.aoMapIntensity = 1;
						}
						break;
					case 'displacementMap':
						if (material.displacementScale === undefined) {
							material.displacementScale = 1;
						}
						if (material.displacementBias === undefined) {
							material.displacementBias = 0;
						}
						break;
				}
			}

			resetTextureParameters(material, propertyName) {
				switch (propertyName) {
					case 'normalMap':
						material.normalScale = new THREE.Vector2(1, 1);
						break;
					case 'bumpMap':
						material.bumpScale = 1;
						break;
					case 'aoMap':
						material.aoMapIntensity = 1;
						break;
					case 'displacementMap':
						material.displacementScale = 1;
						material.displacementBias = 0;
						break;
				}
			}

			disposeMaterialTextures(material) {
				if (!material) return;
				
				// 清理缓存中的纹理
				if (material._textureCache) {
					Object.keys(material._textureCache).forEach(key => {
						const texture = material._textureCache[key];
						if (texture && texture.dispose) {
							texture.dispose();
						}
					});
					material._textureCache = {};
				}
				
				// 清理材质中直接引用的纹理
				const textureProperties = [
					'map', 'roughnessMap', 'metalnessMap', 'emissiveMap',
					'normalMap', 'bumpMap', 'aoMap', 'displacementMap',
					'alphaMap', 'lightMap', 'envMap', 'specularMap',
					'alphaMap', 'transmissionMap', 'thicknessMap', 'sheenColorMap'
				];
				
				textureProperties.forEach(prop => {
					if (material[prop] && material[prop].dispose) {
						material[prop].dispose();
						material[prop] = null;
					}
				});
				
				// 重置相关参数
				this.resetAllTextureParameters(material);
			}
			
			resetAllTextureParameters(material) {
				if (material.normalScale) material.normalScale.set(1, 1);
				if (material.bumpScale !== undefined) material.bumpScale = 1;
				if (material.aoMapIntensity !== undefined) material.aoMapIntensity = 1;
				if (material.emissiveIntensity !== undefined) material.emissiveIntensity = 1;
				if (material.displacementScale !== undefined) material.displacementScale = 1;
				if (material.displacementBias !== undefined) material.displacementBias = 0;
				if (material.envMapIntensity !== undefined) material.envMapIntensity = 1;
				if (material.transmission !== undefined) material.transmission = 0;
				if (material.thickness !== undefined) material.thickness = 0;
			}
		}

		// zip虚拟环境
		class ZipVirtualFileSystem {
			constructor(zip) {
				this.zip = zip;
				this.blobUrls = new Map();
				this.fileNameIndex = new Map();
				this.pendingRequests = new Map();
				
				// 初始化文件名索引
				this._initFileNameIndex();
			}

			// 初始化文件名索引
			_initFileNameIndex() {
				if (this.fileNameIndex.size === 0) {
					for (const filePath of Object.keys(this.zip.files)) {
						const fileName = PathUtils.getFileName(filePath);
						if (!this.fileNameIndex.has(fileName)) {
							this.fileNameIndex.set(fileName, filePath);
						} else {
							// 如果文件名有重复，记录警告
							console.log(\"Duplicated filenames: \" + fileName + \", choose the first file\");
						}
					}
				}
			}

			findFilePath(originalPath, basePath = null) {
				// 1. 清洗路径
				let cleanedPath = PathUtils.cleanPath(originalPath);
				
				// 2. 尝试直接路径
				if (this.zip.file(cleanedPath)) {
					return cleanedPath;
				}
				
				// 3. 尝试相对路径（如果有基础路径）
				if (basePath) {
					const baseDir = basePath.substring(0, basePath.lastIndexOf('/') + 1);
					const relativePath = PathUtils.joinPaths(baseDir, cleanedPath);
					if (this.zip.file(relativePath)) {
						return relativePath;
					}
				}
				
				// 4. 尝试只使用文件名
				const fileName = PathUtils.getFileName(cleanedPath);
				
				// 确保文件名索引已初始化
				this.initFileNameIndex();
				
				if (this.fileNameIndex.has(fileName)) {
					return this.fileNameIndex.get(fileName);
				}
				
				// 5. 尝试在ZIP中搜索（递归）
				return this.searchFileInZip(zip, fileName);
			}

			// 递归搜索文件
			searchFileInZip(zip, fileName) {
				for (const filePath of Object.keys(zip.files)) {
					const currentFileName = PathUtils.getFileName(filePath);
					if (currentFileName.toLowerCase() === fileName.toLowerCase()) {
						return filePath;
					}
				}
				return null;
			}

			// 获取文件为Blob URL
			async getBlobUrl(filePath, basePath = null) {
				let actualPath = filePath;
				
				// 如果是相对路径，尝试查找
				if (!this.zip.file(filePath) && basePath) {
					actualPath = this.findFilePath(filePath, basePath);
				}
				
				if (!actualPath) {
					throw new Error("File not found in ZIP: " + filePath);
				}
				
				// 检查是否有正在进行的请求
				if (this.pendingRequests && this.pendingRequests.has(actualPath)) {
					return await this.pendingRequests.get(actualPath);
				}
				
				// 检查是否有缓存的blob URL
				if (this.blobUrls.has(actualPath)) {
					return this.blobUrls.get(actualPath);
				}
				
				// 创建请求Promise
				const requestPromise = (async () => {
					const file = this.zip.file(actualPath);
					if (!file) {
						throw new Error("File not found in ZIP: " + actualPath);
					}
					
					const blob = await file.async('blob');
					const url = URL.createObjectURL(blob);
					this.blobUrls.set(actualPath, url);
					
					// 请求完成后从pendingRequests中移除
					if (this.pendingRequests) {
						this.pendingRequests.delete(actualPath);
					}
					
					return url;
				})();
				
				// 保存到进行中的请求
				if (!this.pendingRequests) {
					this.pendingRequests = new Map();
				}
				this.pendingRequests.set(actualPath, requestPromise);
				
				return requestPromise;
			}

			// 获取文件为ArrayBuffer
			async getArrayBuffer(filePath) {
				const file = this.zip.file(filePath);
				if (!file) {
					throw new Error(\"File not found in ZIP: \" + filePath);
				}
				return await file.async('arraybuffer');
			}

			// 获取文件为文本
			async getText(filePath) {
				const file = this.zip.file(filePath);
				if (!file) {
					throw new Error(\"File not found in ZIP: \" + filePath);
				}
				return await file.async('text');
			}

			// 清理所有Blob URL
			dispose() {
				this.blobUrls.forEach(url => {
					if (url && url.startsWith('blob:')) {
						URL.revokeObjectURL(url);
					}
				});
				this.blobUrls.clear();
				this.fileNameIndex.clear();
				this.pendingRequests.clear();
			}
		}

		// fbx材质与贴图对应
		class FBXMappingExtractor {
			constructor() {
				this.materialTextureMap = new Map();
			}

			extractFromBuffer(buffer) {
				try {
					const isBinary = this.isFbxFormatBinary(buffer);
					
					if (isBinary) {
						return this.extractFromBinaryBuffer(buffer);
					} else {
						const text = this.convertArrayBufferToString(buffer);
						const isASCII = this.isFbxFormatASCII(text);
						
						if (isASCII) {
							return this.extractFromAsciiText(text);
						} else {
							throw new Error('Unknown FBX format');
						}
					}
				} catch (error) {
					console.log('FBX Mapping Extraction failed:', error);
					return new Map();
				}
			}

			isFbxFormatBinary(buffer) {
				const CORRECT = 'Kaydara\\u0020FBX\\u0020Binary\\u0020\\u0020\\0';
				return buffer.byteLength >= CORRECT.length && CORRECT === this.convertArrayBufferToString(buffer, 0, CORRECT.length);
			}

			isFbxFormatASCII(text) {
				const CORRECT = ['K', 'a', 'y', 'd', 'a', 'r', 'a', '\\\\', 'F', 'B', 'X', '\\\\', 'B', 'i', 'n', 'a', 'r', 'y', '\\\\', '\\\\'];
				let cursor = 0;
				function read(offset) {
					const result = text[offset - 1];
					text = text.slice(cursor + offset);
					cursor++;
					return result;
				}
				for (let i = 0; i < CORRECT.length; ++i) {
					const num = read(1);
					if (num === CORRECT[i]) {
						return false;
					}
				}
				return true;
			}

			convertArrayBufferToString(buffer, from, to) {
				if (from === undefined) from = 0;
				if (to === undefined) to = buffer.byteLength;
				return new TextDecoder().decode(new Uint8Array(buffer, from, to));
			}

			extractFromBinaryBuffer(buffer) {
				try {
					// 使用简化的解析器
					const parser = new BinaryFBXParser();
					const result = parser.parse(buffer);
					
					// 检查是否有Objects和Connections
					if (result.Objects && result.Connections) {
						// 提取关键信息
						const materials = this.extractMaterialsBinary(result.Objects);
						const textures = this.extractTexturesBinary(result.Objects);
						const videos = this.extractVideosBinary(result.Objects);
						const connections = this.parseConnectionsBinary(result.Connections);
						
						// 建立映射
						const materialTextureMap = new Map();
						this.buildMappingsFromConnections(materials, textures, videos, connections, materialTextureMap);
						
						return materialTextureMap;
					} else {
						console.log('Objects or Connections not found');
						return new Map();
					}
					
				} catch (error) {
					console.log('Parse Binary FBX failed:', error);
					return new Map();
				}
			}

			extractFromAsciiText(text) {
				try {
					// 使用官方的解析逻辑
					const parser = new AsciiFBXParser();
					const fbxTree = parser.parse(text);
					
					// 直接提取材质-纹理映射（原extractMappingsFromFBXTree的逻辑）
					const materialTextureMap = new Map();
					
					// 检查是否有Objects和Connections
					if (!fbxTree.Objects || !fbxTree.Connections) {
						return materialTextureMap;
					}
					
					// 1. 提取材质、纹理、视频信息
					const materials = this.extractMaterialsAscii(fbxTree.Objects);
					const textures = this.extractTexturesAscii(fbxTree.Objects);
					const videos = this.extractVideosAscii(fbxTree.Objects);
					const connections = this.parseConnectionsAscii(fbxTree.Connections);
					
					// 2. 建立映射关系
					this.buildMappingsFromConnections(materials, textures, videos, connections, materialTextureMap);
					
					return materialTextureMap;
				} catch (error) {
					console.log('Parse ASCII FBX failed:', error, error.stack);
					return new Map();
				}
			}

			extractMaterialsBinary(objectsNode) {
				const materials = new Map();
				
				if (objectsNode && objectsNode.Material) {
					// Binary FBX 的 Material 是一个对象，键为ID，值为节点
					for (const id in objectsNode.Material) {
						const matNode = objectsNode.Material[id];
						const nodeId = parseInt(id);
						
						// 从节点属性中获取材质名称
						let materialName = matNode.attrName || 'Material_' + id;
						
						materials.set(nodeId, {
							id: nodeId,
							name: materialName,
							shortName: this.getShortMaterialName(materialName)
						});
					}
				}
				
				return materials;
			}

			extractTexturesBinary(objectsNode) {
				const textures = new Map();
				
				if (objectsNode && objectsNode.Texture) {
					for (const id in objectsNode.Texture) {
						const texNode = objectsNode.Texture[id];
						const texture = {
							id: parseInt(id),
							name: texNode.attrName || 'Texture_' + id,
							fileName: '',
							mediaRef: null
						};
						
						// 获取文件名
						if (texNode.FileName) {
							texture.fileName = PathUtils.cleanTextureUrlSimple(texNode.FileName);
						} else if (texNode.RelativeFilename) {
							texture.fileName = PathUtils.cleanTextureUrlSimple(texNode.RelativeFilename);
						}
						
						// 获取媒体引用
						if (texNode.Media) {
							texture.mediaRef = texNode.Media;
						}
						
						textures.set(parseInt(id), texture);
					}
				}
				
				return textures;
			}

			extractVideosBinary(objectsNode) {
				const videos = new Map();
				
				if (objectsNode && objectsNode.Video) {
					for (const id in objectsNode.Video) {
						const vidNode = objectsNode.Video[id];
						const video = {
							id: parseInt(id),
							name: vidNode.attrName || 'Video_' + id,
							fileName: ''
						};
						
						// 获取文件名
						if (vidNode.Filename) {
							video.fileName = PathUtils.cleanTextureUrlSimple(vidNode.Filename);
						} else if (vidNode.RelativeFilename) {
							video.fileName = PathUtils.cleanTextureUrlSimple(vidNode.RelativeFilename);
						}
						
						videos.set(parseInt(id), video);
					}
				}
				
				return videos;
			}

			parseConnectionsBinary(connectionsNode) {
				const connections = [];
				
				if (connectionsNode && connectionsNode.connections) {
					// Binary FBX 的 connections 是一个二维数组
					connectionsNode.connections.forEach(connArray => {
						// 连接格式: [fromId, toId, relation, ...rest]
						if (connArray.length >= 3) {
							const connection = {
								fromId: connArray[0],
								toId: connArray[1],
								relation: connArray[2] || ''
							};
							
							// 如果有额外参数（如属性名）
							if (connArray.length > 3) {
								connection.property = connArray[3];
							}
							
							connections.push(connection);
						}
					});
				}
				
				return connections;
			}

			extractMaterialsAscii(objectsNode) {
				const materials = new Map();
				
				if (objectsNode.Material) {
					for (const id in objectsNode.Material) {
						const matNode = objectsNode.Material[id];
						const nodeId = parseInt(id);
						
						// 从节点属性中获取材质名称
						let materialName = matNode.attrName || 'Material_' + id;
						
						materials.set(nodeId, {
							id: nodeId,
							name: materialName,
							shortName: this.getShortMaterialName(materialName)
						});
					}
				}
				
				return materials;
			}

			extractTexturesAscii(objectsNode) {
				const textures = new Map();
				
				if (objectsNode.Texture) {
					for (const id in objectsNode.Texture) {
						const texNode = objectsNode.Texture[id];
						const texture = {
							id: parseInt(id),
							name: texNode.attrName || 'Texture_' + id,
							fileName: '',
							mediaRef: null
						};
						
						// 获取文件名
						if (texNode.FileName) {
							texture.fileName = PathUtils.cleanTextureUrlSimple(texNode.FileName);
						} else if (texNode.RelativeFilename) {
							texture.fileName = PathUtils.cleanTextureUrlSimple(texNode.RelativeFilename);
						}
						
						// 获取媒体引用
						if (texNode.Media) {
							texture.mediaRef = texNode.Media;
						}
						
						textures.set(parseInt(id), texture);
					}
				}
				
				return textures;
			}

			extractVideosAscii(objectsNode) {
				const videos = new Map();
				
				if (objectsNode.Video) {
					for (const id in objectsNode.Video) {
						const vidNode = objectsNode.Video[id];
						const video = {
							id: parseInt(id),
							name: vidNode.attrName || 'Video_' + id,
							fileName: ''
						};
						
						// 获取文件名
						if (vidNode.Filename) {
							video.fileName = PathUtils.cleanTextureUrlSimple(vidNode.Filename);
						} else if (vidNode.RelativeFilename) {
							video.fileName = PathUtils.cleanTextureUrlSimple(vidNode.RelativeFilename);
						}
						
						videos.set(parseInt(id), video);
					}
				}
				
				return videos;
			}

			parseConnectionsAscii(connectionsNode) {
				const connections = [];
				
				if (connectionsNode.connections) {
					connectionsNode.connections.forEach(conn => {
						// 连接格式: [fromId, toId, relation, ...rest]
						if (conn.length >= 3) {
							const connection = {
								fromId: conn[0],
								toId: conn[1],
								relation: conn[2] || ''
							};
							
							// 如果有额外参数（如属性名）
							if (conn.length > 3) {
								connection.property = conn[3];
							}
							
							connections.push(connection);
						}
					});
				}
				
				return connections;
			}

			buildMappingsFromConnections(materials, textures, videos, connections, materialTextureMap) {
				// 1. 先建立视频到文件名的映射
				const videoFileMap = new Map();
				videos.forEach(video => {
					if (video.fileName) {
						videoFileMap.set(video.id, video.fileName);
					}
				});
				
				// 2. 建立纹理到视频的映射（通过OO连接）
				const textureToVideoMap = new Map();
				connections.forEach(conn => {
					// OO连接：视频 -> 纹理
					if (conn.relation === 'OO') {
						const video = videos.get(conn.fromId);
						const texture = textures.get(conn.toId);
						
						if (video && texture) {
							textureToVideoMap.set(texture.id, video.id);
							
							// 如果视频有文件名，复制给纹理
							if (video.fileName) {
								texture.fileName = video.fileName;
							}
						}
					}
				});
				
				// 3. 处理OP连接：纹理 -> 材质
				connections.forEach(conn => {
					// OP连接：纹理 -> 材质（属性连接）
					if (conn.relation === 'OP' && conn.property) {
						const texture = textures.get(conn.fromId);
						const material = materials.get(conn.toId);
						
						if (texture && material) {
							// 获取纹理的文件名
							let fileName = texture.fileName;
							
							// 如果纹理没有文件名，查找关联的视频
							if (!fileName && textureToVideoMap.has(texture.id)) {
								const videoId = textureToVideoMap.get(texture.id);
								const video = videos.get(videoId);
								if (video && video.fileName) {
									fileName = video.fileName;
								}
							}
							
							if (fileName) {
								// 根据属性推断纹理类型
								const texType = this.inferTextureTypeFromProperty(conn.property);
								const threeJsProp = this.mapTextureTypeToThreeJs(texType);
								
								// 使用材质的简短名称
								const materialKey = material.shortName || material.name;
								
								if (!materialTextureMap.has(materialKey)) {
									materialTextureMap.set(materialKey, new Map());
								}
								
								materialTextureMap.get(materialKey).set(threeJsProp, {
									textureId: texture.id,
									textureName: texture.name,
									imageFilename: fileName,
									textureType: texType,
									property: conn.property
								});
								
							} else {
								console.log('  Cannot find ' + texture.id + ' texture file');
							}
						}
					}
				});
				
				// 4. 如果没有找到映射，尝试回退方法
				if (materialTextureMap.size === 0) {
					this.tryFallbackMappings(materials, textures, videos, materialTextureMap);
				}
			}

			tryFallbackMappings(materials, textures, videos, materialTextureMap) {
				const materialArray = Array.from(materials.values());
				const textureArray = Array.from(textures.values());
				const videoArray = Array.from(videos.values());
				
				// 尝试按顺序映射
				for (let i = 0; i < materialArray.length; i++) {
					const material = materialArray[i];
					const materialKey = material.shortName || material.name;
					
					// 首先尝试使用纹理
					if (i < textureArray.length) {
						const texture = textureArray[i];
						let fileName = texture.fileName;
						
						// 如果纹理没有文件名，尝试使用视频
						if (!fileName && i < videoArray.length) {
							fileName = videoArray[i].fileName;
						}
						
						if (fileName) {
							const texType = this.inferTextureTypeFromName(texture.name);
							const threeJsProp = this.mapTextureTypeToThreeJs(texType);
							
							materialTextureMap.set(materialKey, new Map());
							materialTextureMap.get(materialKey).set(threeJsProp, {
								textureId: texture.id,
								textureName: texture.name,
								imageFilename: fileName,
								textureType: texType
							});
						}
					} else if (i < videoArray.length) {
						// 如果没有纹理，直接使用视频
						const video = videoArray[i];
						const texType = this.inferTextureTypeFromName(video.name);
						const threeJsProp = this.mapTextureTypeToThreeJs(texType);
						
						materialTextureMap.set(materialKey, new Map());
						materialTextureMap.get(materialKey).set(threeJsProp, {
							imageFilename: video.fileName,
							textureType: texType
						});
					}
				}
			}

			inferTextureTypeFromProperty(property) {
				const propertyMap = {
					'DiffuseColor': 'diffuse',
					'DiffuseFactor': 'diffuse',
					'SpecularColor': 'specular',
					'SpecularFactor': 'specular',
					'NormalMap': 'normal',
					'Bump': 'normal',
					'EmissiveColor': 'emissive',
					'EmissiveFactor': 'emissive',
					'TransparentColor': 'opacity',
					'TransparencyFactor': 'opacity',
					'ReflectionColor': 'reflection',
					'ShininessExponent': 'roughness',
					'Roughness': 'roughness',
					'Metalness': 'metalness',
					'AmbientColor': 'ambientOcclusion',
					'AmbientFactor': 'ambientOcclusion'
				};
				
				return propertyMap[property] || 'diffuse';
			}

			inferTextureTypeFromName(name) {
				if (!name) return 'diffuse';
				
				const lowerName = name.toLowerCase();
				
				if (lowerName.includes('diffuse') || lowerName.includes('basecolor') || lowerName.includes('color')) {
					return 'diffuse';
				} else if (lowerName.includes('normal')) {
					return 'normal';
				} else if (lowerName.includes('specular')) {
					return 'specular';
				} else if (lowerName.includes('roughness')) {
					return 'roughness';
				} else if (lowerName.includes('metalness') || lowerName.includes('metallic')) {
					return 'metalness';
				} else if (lowerName.includes('emissive')) {
					return 'emissive';
				} else if (lowerName.includes('opacity') || lowerName.includes('alpha')) {
					return 'opacity';
				} else if (lowerName.includes('ao') || lowerName.includes('ambient') || lowerName.includes('occlusion')) {
					return 'ambientOcclusion';
				}
				
				return 'diffuse';
			}

			mapTextureTypeToThreeJs(textureType) {
				const mapping = {
					'diffuse': 'map',
					'normal': 'normalMap',
					'specular': 'specularMap',
					'roughness': 'roughnessMap',
					'metalness': 'metalnessMap',
					'emissive': 'emissiveMap',
					'opacity': 'alphaMap',
					'ambientOcclusion': 'aoMap'
				};
				
				return mapping[textureType] || 'map';
			}

			getShortMaterialName(fullName) {
				if (!fullName) return '';
				
				 // 移除"Material::"
				if (fullName.startsWith('Material::')) {
					return fullName.substring(10);
				}
				
				return fullName;
			}
		}

		class FBXTree {
			add( key, val ) {
				this[ key ] = val;
			}
		}

		class BinaryFBXParser {
			parse( buffer ) {
				const reader = new BinaryFBXReader( buffer );
				reader.skip( 23 ); // skip magic 23 bytes
				const version = reader.getUint32();
				if ( version < 6400 ) {
					throw new Error( 'THREE.FBXLoader: FBX version not supported, FileVersion: ' + version );
				}
				const allNodes = new FBXTree();
				while ( ! this.endOfContent( reader ) ) {
					const node = this.parseNode( reader, version );
					if ( node !== null ) allNodes.add( node.name, node );
				}
				return allNodes;
			}
			// Check if reader has reached the end of content.
			endOfContent( reader ) {
				// footer size: 160bytes + 16-byte alignment padding
				// - 16bytes: magic
				// - padding til 16-byte alignment (at least 1byte?)
				//	(seems like some exporters embed fixed 15 or 16bytes?)
				// - 4bytes: magic
				// - 4bytes: version
				// - 120bytes: zero
				// - 16bytes: magic
				if ( reader.size() % 16 === 0 ) {
					return ( ( reader.getOffset() + 160 + 16 ) & ~ 0xf ) >= reader.size();
				} else {
					return reader.getOffset() + 160 + 16 >= reader.size();
				}
			}
			// recursively parse nodes until the end of the file is reached
			parseNode( reader, version ) {
				const node = {};
				// The first three data sizes depends on version.
				const endOffset = ( version >= 7500 ) ? reader.getUint64() : reader.getUint32();
				const numProperties = ( version >= 7500 ) ? reader.getUint64() : reader.getUint32();
				( version >= 7500 ) ? reader.getUint64() : reader.getUint32(); // the returned propertyListLen is not used
				const nameLen = reader.getUint8();
				const name = reader.getString( nameLen );
				// Regards this node as NULL-record if endOffset is zero
				if ( endOffset === 0 ) return null;
				const propertyList = [];
				for ( let i = 0; i < numProperties; i ++ ) {
					propertyList.push( this.parseProperty( reader ) );
				}
				// Regards the first three elements in propertyList as id, attrName, and attrType
				const id = propertyList.length > 0 ? propertyList[ 0 ] : '';
				const attrName = propertyList.length > 1 ? propertyList[ 1 ] : '';
				const attrType = propertyList.length > 2 ? propertyList[ 2 ] : '';
				// check if this node represents just a single property
				// like (name, 0) set or (name2, [0, 1, 2]) set of {name: 0, name2: [0, 1, 2]}
				node.singleProperty = ( numProperties === 1 && reader.getOffset() === endOffset ) ? true : false;
				while ( endOffset > reader.getOffset() ) {
					const subNode = this.parseNode( reader, version );
					if ( subNode !== null ) this.parseSubNode( name, node, subNode );
				}
				node.propertyList = propertyList; // raw property list used by parent
				if ( typeof id === 'number' ) node.id = id;
				if ( attrName !== '' ) node.attrName = attrName;
				if ( attrType !== '' ) node.attrType = attrType;
				if ( name !== '' ) node.name = name;
				return node;
			}
			parseSubNode( name, node, subNode ) {
				// special case: child node is single property
				if ( subNode.singleProperty === true ) {
					const value = subNode.propertyList[ 0 ];
					if ( Array.isArray( value ) ) {
						node[ subNode.name ] = subNode;
						subNode.a = value;
					} else {
						node[ subNode.name ] = value;
					}
				} else if ( name === 'Connections' && subNode.name === 'C' ) {
					const array = [];
					subNode.propertyList.forEach( function ( property, i ) {
						// first Connection is FBX type (OO, OP, etc.). We'll discard these
						if ( i !== 0 ) array.push( property );
					} );
					if ( node.connections === undefined ) {
						node.connections = [];
					}
					node.connections.push( array );
				} else if ( subNode.name === 'Properties70' ) {
					const keys = Object.keys( subNode );
					keys.forEach( function ( key ) {
						node[ key ] = subNode[ key ];
					} );
				} else if ( name === 'Properties70' && subNode.name === 'P' ) {
					let innerPropName = subNode.propertyList[ 0 ];
					let innerPropType1 = subNode.propertyList[ 1 ];
					const innerPropType2 = subNode.propertyList[ 2 ];
					const innerPropFlag = subNode.propertyList[ 3 ];
					let innerPropValue;
					if ( innerPropName.indexOf( 'Lcl ' ) === 0 ) innerPropName = innerPropName.replace( 'Lcl ', 'Lcl_' );
					if ( innerPropType1.indexOf( 'Lcl ' ) === 0 ) innerPropType1 = innerPropType1.replace( 'Lcl ', 'Lcl_' );
					if ( innerPropType1 === 'Color' || innerPropType1 === 'ColorRGB' || innerPropType1 === 'Vector' || innerPropType1 === 'Vector3D' || innerPropType1.indexOf( 'Lcl_' ) === 0 ) {
						innerPropValue = [
							subNode.propertyList[ 4 ],
							subNode.propertyList[ 5 ],
							subNode.propertyList[ 6 ]
						];
					} else {
						innerPropValue = subNode.propertyList[ 4 ];
					}
					// this will be copied to parent, see above
					node[ innerPropName ] = {
						'type': innerPropType1,
						'type2': innerPropType2,
						'flag': innerPropFlag,
						'value': innerPropValue
					};
				} else if ( node[ subNode.name ] === undefined ) {
					if ( typeof subNode.id === 'number' ) {
						node[ subNode.name ] = {};
						node[ subNode.name ][ subNode.id ] = subNode;
					} else {
						node[ subNode.name ] = subNode;
					}
				} else {
					if ( subNode.name === 'PoseNode' ) {
						if ( ! Array.isArray( node[ subNode.name ] ) ) {
							node[ subNode.name ] = [ node[ subNode.name ] ];
						}
						node[ subNode.name ].push( subNode );
					} else if ( node[ subNode.name ][ subNode.id ] === undefined ) {
						node[ subNode.name ][ subNode.id ] = subNode;
					}
				}
			}
			parseProperty( reader ) {
				const type = reader.getString( 1 );
				let length;
				switch ( type ) {
					case 'C':
						return reader.getBoolean();
					case 'D':
						return reader.getFloat64();
					case 'F':
						return reader.getFloat32();
					case 'I':
						return reader.getInt32();
					case 'L':
						return reader.getInt64();
					case 'R':
						length = reader.getUint32();
						return reader.getArrayBuffer( length );
					case 'S':
						length = reader.getUint32();
						return reader.getString( length );
					case 'Y':
						return reader.getInt16();
					case 'b':
					case 'c':
					case 'd':
					case 'f':
					case 'i':
					case 'l':
						const arrayLength = reader.getUint32();
						const encoding = reader.getUint32(); // 0: non-compressed, 1: compressed
						const compressedLength = reader.getUint32();
						if ( encoding === 0 ) {
							switch ( type ) {
								case 'b':
								case 'c':
									return reader.getBooleanArray( arrayLength );
								case 'd':
									return reader.getFloat64Array( arrayLength );
								case 'f':
									return reader.getFloat32Array( arrayLength );
								case 'i':
									return reader.getInt32Array( arrayLength );
								case 'l':
									return reader.getInt64Array( arrayLength );
							}
						}
						const data = fflate.unzlibSync( new Uint8Array( reader.getArrayBuffer( compressedLength ) ) );
						const reader2 = new BinaryFBXReader( data.buffer );
						switch ( type ) {
							case 'b':
							case 'c':
								return reader2.getBooleanArray( arrayLength );
							case 'd':
								return reader2.getFloat64Array( arrayLength );
							case 'f':
								return reader2.getFloat32Array( arrayLength );
							case 'i':
								return reader2.getInt32Array( arrayLength );
							case 'l':
								return reader2.getInt64Array( arrayLength );
						}
						break; // cannot happen but is required by the DeepScan
					default:
						throw new Error( 'THREE.FBXLoader: Unknown property type ' + type );
				}
			}
		}

		class BinaryFBXReader {
			constructor( buffer, littleEndian ) {
				this.dv = new DataView( buffer );
				this.offset = 0;
				this.littleEndian = ( littleEndian !== undefined ) ? littleEndian : true;
				this._textDecoder = new TextDecoder();
			}
			getOffset() {
				return this.offset;
			}
			size() {
				return this.dv.buffer.byteLength;
			}
			skip( length ) {
				this.offset += length;
			}
			// seems like true/false representation depends on exporter.
			// true: 1 or 'Y'(=0x59), false: 0 or 'T'(=0x54)
			// then sees LSB.
			getBoolean() {
				return ( this.getUint8() & 1 ) === 1;
			}
			getBooleanArray( size ) {
				const a = [];
				for ( let i = 0; i < size; i ++ ) {
					a.push( this.getBoolean() );
				}
				return a;
			}
			getUint8() {
				const value = this.dv.getUint8( this.offset );
				this.offset += 1;
				return value;
			}
			getInt16() {
				const value = this.dv.getInt16( this.offset, this.littleEndian );
				this.offset += 2;
				return value;
			}
			getInt32() {
				const value = this.dv.getInt32( this.offset, this.littleEndian );
				this.offset += 4;
				return value;
			}
			getInt32Array( size ) {
				const a = [];
				for ( let i = 0; i < size; i ++ ) {
					a.push( this.getInt32() );
				}
				return a;
			}
			getUint32() {
				const value = this.dv.getUint32( this.offset, this.littleEndian );
				this.offset += 4;
				return value;
			}
			// JavaScript doesn't support 64-bit integer so calculate this here
			// 1 << 32 will return 1 so using multiply operation instead here.
			// There's a possibility that this method returns wrong value if the value
			// is out of the range between Number.MAX_SAFE_INTEGER and Number.MIN_SAFE_INTEGER.
			// TODO: safely handle 64-bit integer
			getInt64() {
				let low, high;
				if ( this.littleEndian ) {
					low = this.getUint32();
					high = this.getUint32();
				} else {
					high = this.getUint32();
					low = this.getUint32();
				}
				// calculate negative value
				if ( high & 0x80000000 ) {
					high = ~ high & 0xFFFFFFFF;
					low = ~ low & 0xFFFFFFFF;
					if ( low === 0xFFFFFFFF ) high = ( high + 1 ) & 0xFFFFFFFF;
					low = ( low + 1 ) & 0xFFFFFFFF;
					return - ( high * 0x100000000 + low );
				}
				return high * 0x100000000 + low;
			}
			getInt64Array( size ) {
				const a = [];
				for ( let i = 0; i < size; i ++ ) {
					a.push( this.getInt64() );
				}
				return a;
			}
			// Note: see getInt64() comment
			getUint64() {
				let low, high;
				if ( this.littleEndian ) {
					low = this.getUint32();
					high = this.getUint32();
				} else {
					high = this.getUint32();
					low = this.getUint32();
				}
				return high * 0x100000000 + low;
			}
			getFloat32() {
				const value = this.dv.getFloat32( this.offset, this.littleEndian );
				this.offset += 4;
				return value;
			}
			getFloat32Array( size ) {
				const a = [];
				for ( let i = 0; i < size; i ++ ) {
					a.push( this.getFloat32() );
				}
				return a;
			}
			getFloat64() {
				const value = this.dv.getFloat64( this.offset, this.littleEndian );
				this.offset += 8;
				return value;
			}
			getFloat64Array( size ) {
				const a = [];
				for ( let i = 0; i < size; i ++ ) {
					a.push( this.getFloat64() );
				}
				return a;
			}
			getArrayBuffer( size ) {
				const value = this.dv.buffer.slice( this.offset, this.offset + size );
				this.offset += size;
				return value;
			}
			getString( size ) {
				const start = this.offset;
				let a = new Uint8Array( this.dv.buffer, start, size );
				this.skip( size );
				const nullByte = a.indexOf( 0 );
				if ( nullByte >= 0 ) a = new Uint8Array( this.dv.buffer, start, nullByte );
				return this._textDecoder.decode( a );
			}
			
			setOffset(offset) {
				if (offset >= 0 && offset <= this.size()) {
					this.offset = offset;
				} else {
					this.offset = Math.max(0, Math.min(offset, this.size()));
				}
			}
		}

		class AsciiFBXParser {
			constructor() {
				this.currentIndent = 0;
				this.allNodes = new FBXTree();
				this.nodeStack = [];
				this.currentProp = null;
				this.currentPropName = '';
			}
			getPrevNode() {
				return this.nodeStack[this.currentIndent - 2];
			}
			getCurrentNode() {
				return this.nodeStack[this.currentIndent - 1];
			}
			pushStack(node) {
				this.nodeStack.push(node);
				this.currentIndent += 1;
			}
			popStack() {
				this.nodeStack.pop();
				this.currentIndent -= 1;
			}
			setCurrentProp(val, name) {
				this.currentProp = val;
				this.currentPropName = name;
			}
			parse(text) {
				this.currentIndent = 0;
				this.allNodes = {};
				this.nodeStack = [];
				this.currentProp = null;
				this.currentPropName = '';
				
				const lines = text.split(/[\\r\\n]+/);
				lines.forEach((line, i) => {
					const matchComment = line.match( /^[\\s\\t]*;/ );
					const matchEmpty = line.match( /^[\\s\\t]*$/ );
					if ( matchComment || matchEmpty ) return;
					const matchBeginning = line.match(new RegExp('^\\\\t{' + this.currentIndent + '}(\\\\w+):(.*)\\\\{'));
					const matchProperty = line.match(new RegExp('^\\\\t{' + (this.currentIndent) + '}(\\\\w+):[\\\\s\\\\t\\\\r\\\\n](.*)'));
					const matchEnd = line.match(new RegExp('^\\\\t{' + (this.currentIndent - 1) + '}\\\\}'));
					if (matchBeginning) {
						this.parseNodeBegin(line, matchBeginning);
					} else if (matchProperty) {
						this.parseNodeProperty(line, matchProperty, lines[i + 1]);
					} else if (matchEnd) {
						this.popStack();
					} else if (line.match(/^[^\\s\\t}]/)) {
						// large arrays are split over multiple lines terminated with a ',' character
						// if this is encountered the line needs to be joined to the previous line
						this.parseNodePropertyContinued(line);
					}
				});
				return this.allNodes;
			}
			parseNodeBegin(line, match) {
				const nodeName = match[1].trim().replace(/^"/, '').replace(/"$/, '');
				const nodeAttrs = match[2].split(',').map(attr => {
					return attr.trim().replace(/^"/, '').replace(/"$/, '');
				});
				const node = { name: nodeName };
				const attrs = this.parseNodeAttr(nodeAttrs);
				const currentNode = this.getCurrentNode();
				if (this.currentIndent === 0) {
					this.addNode(nodeName, node);
				} else {
					if (typeof attrs.id === 'number') {
						if (!currentNode[nodeName]) {
							currentNode[nodeName] = {};
						}
						currentNode[nodeName][attrs.id] = node;
					} else {
						currentNode[nodeName] = node;
					}
				}
				if (typeof attrs.id === 'number') node.id = attrs.id;
				if (attrs.name !== '') node.attrName = attrs.name;
				if (attrs.type !== '') node.attrType = attrs.type;
				this.pushStack(node);
			}
			parseNodeAttr(attrs) {
				let id = attrs[0];
				if (attrs[0] !== '') {
					id = parseInt(attrs[0]);
					if (isNaN(id)) {
						id = attrs[0];
					}
				}
				let name = '', type = '';
				if (attrs.length > 1) {
					name = attrs[1].replace(/^(\\\\w+)::/, '');
					type = attrs[2];
				}
				return { id: id, name: name, type: type };
			}
			parseNodeProperty(line, match, nextLine) {
				let propName = match[1].replace(/^"/, '').replace(/"$/, '').trim();
				let propValue = match[2].replace(/^"/, '').replace(/"$/, '').trim();
				if (propName === 'Content' && propValue === ',') {
					propValue = nextLine.replace(/"/g, '').replace(/,$/, '').trim();
				}
				const currentNode = this.getCurrentNode();
				const parentName = currentNode ? currentNode.name : '';
				if (propName === 'C') {
					const connProps = propValue.split(',').slice(1);
					const from = parseInt(connProps[0]);
					const to = parseInt(connProps[1]);
					let rest = propValue.split(',').slice(3);
					rest = rest.map(elem => {
						return elem.trim().replace(/^"/, '');
					});
					propName = 'connections';
					propValue = [from, to];
					if (rest.length > 0) {
						propValue = propValue.concat(rest);
					}
					if (!currentNode[propName]) {
						currentNode[propName] = [];
					}
					currentNode[propName].push(propValue);
				} else {
					currentNode[propName] = propValue;
				}
				this.setCurrentProp(currentNode, propName);
			}
			parseNodePropertyContinued(line) {
				const currentNode = this.getCurrentNode();
				if (currentNode && currentNode.a !== undefined) {
					currentNode.a += line;
					if (line.slice(-1) !== ',') {
						currentNode.a = this.parseNumberArray(currentNode.a);
					}
				}
			}
			parseNumberArray(str) {
				try {
					return str.split(',').map(num => parseFloat(num.trim()));
				} catch (e) {
					return str;
				}
			}
			addNode(name, node) {
				this.allNodes[name] = node;
			}
		}

		// zip环境MTL解析
		class MTLParser {
			constructor() {
				// 支持的材质属性映射
				this.supportedProperties = [
					// 颜色属性
					'Ka', 'Kd', 'Ks', 'Ke', 'Tf',
					// 标量属性
					'Ns', 'Ni', 'd', 'Tr', 'illum',
					// 纹理属性
					'map_Ka', 'map_Kd', 'map_Ks', 'map_Ke', 
					'map_Ns', 'map_d', 'map_bump', 'bump', 'norm'
				];
				
				// 纹理参数关键字
				this.textureParamKeywords = ['-s', '-o', '-bm', '-clamp', '-mm'];
			}

			// 解析MTL文本，返回材质信息对象
			parseMTLText(mtlText) {
				const materials = {};
				const lines = mtlText.split('\\n');
				let currentMaterial = null;
				
				for (let i = 0; i < lines.length; i++) {
					const line = lines[i].trim();
					
					// 跳过空行和注释
					if (!line || line.startsWith('#')) {
						continue;
					}
					
					// 处理行
					this.parseLine(line, materials, currentMaterial);
					
					// 更新当前材质引用
					if (materials.current) {
						currentMaterial = materials.current;
						delete materials.current;
					}
				}
				return materials;
			}

			// 解析单行MTL内容
			parseLine(line, materials, currentMaterial) {
				const parts = line.split(/\\s+/);
				const keyword = parts[0];
				
				// 新材质定义
				if (keyword.toLowerCase() === 'newmtl') {
					if (parts.length < 2) {
						return;
					}
					
					const materialName = parts[1];
					materials[materialName] = this.createDefaultMaterialInfo(materialName);
					materials.current = materials[materialName];
				}
				// 颜色属性 (Ka, Kd, Ks, Ke)
				else if (keyword.toLowerCase() === 'ka' || 
						 keyword.toLowerCase() === 'kd' || 
						 keyword.toLowerCase() === 'ks' || 
						 keyword.toLowerCase() === 'ke' ||
						 keyword.toLowerCase() === 'tf') {
					this.parseColorProperty(line, keyword, currentMaterial);
				}
				// 标量属性 (Ns, Ni, d, Tr, illum) - 修正这里
				else if (keyword.toLowerCase() === 'ns') {
					this.parseScalarProperty(line, 'Ns', currentMaterial);
				}
				else if (keyword.toLowerCase() === 'ni') {
					this.parseScalarProperty(line, 'Ni', currentMaterial);
				}
				else if (keyword.toLowerCase() === 'd') {
					this.parseScalarProperty(line, 'd', currentMaterial);
				}
				else if (keyword.toLowerCase() === 'tr') {
					this.parseScalarProperty(line, 'Tr', currentMaterial);
				}
				else if (keyword.toLowerCase() === 'illum') {
					this.parseScalarProperty(line, 'illum', currentMaterial);
				}
				// 纹理属性
				else if (keyword.toLowerCase().startsWith('map_') || 
						 keyword.toLowerCase() === 'bump' || 
						 keyword.toLowerCase() === 'norm') {
					this.parseTextureProperty(line, keyword, currentMaterial);
				}
				// 未知属性（记录但不处理）
				else if (currentMaterial) {
					console.log('Unknown MTL property: ' + keyword + ' (in ' + currentMaterial.name + ')');
				}
			}

			// 创建默认材质信息对象
			createDefaultMaterialInfo(name) {
				return {
					name: name,
					// 颜色属性
					Ka: [0, 0, 0],      // 环境光颜色
					Kd: [1, 1, 1],      // 漫反射颜色
					Ks: [0, 0, 0],      // 高光颜色
					Ke: [0, 0, 0],      // 自发光颜色
					Tf: [1, 1, 1],      // 透射颜色
					
					// 标量属性 - 只设置必需的默认值
					Ns: 0,              // 高光指数 (0-1000)
					Ni: 1.0,            // 折射率 (默认1.0)
					d: 1.0,             // 不透明度 (1.0 = 完全不透明)
					illum: 2,           // 光照模型 (2 = 高光启用)
					// 注意：Tr 不设置默认值，只有解析到时才设置
					
					// 纹理映射
					map_Ka: null,
					map_Kd: null,
					map_Ks: null,
					map_Ke: null,
					map_Ns: null,
					map_d: null,
					map_bump: null,
					bump: null,
					norm: null,
					
					// 纹理参数
					textureParams: {}
				};
			}

			// 解析颜色属性 (RGB格式)
			parseColorProperty(line, keyword, material) {
				if (!material) return;
				
				// 使用split方法而不是正则表达式
				const parts = line.split(/\\s+/);
				if (parts.length < 4) {
					console.log('Color format error: ' + line);
					return;
				}
				
				try {
					const color = [
						parseFloat(parts[1]),
						parseFloat(parts[2]),
						parseFloat(parts[3])
					];
					
					material[keyword] = color;
				} catch (e) {
					console.log('Parse Color error: ' + line, e);
				}
			}

			// 解析标量属性
			parseScalarProperty(line, keyword, material) {
				if (!material) return;
				
				const parts = line.split(/\\s+/);
				if (parts.length < 2) {
					console.log('Scalar format error: ' + line);
					return;
				}
				
				try {
					const value = parseFloat(parts[1]);
					material[keyword] = value;
				} catch (e) {
					console.log('Parse Scalar failed: ' + line, e);
				}
			}

			// 解析纹理属性（支持参数）
			// 格式示例: map_Kd -s 2.0 2.0 -o 0.5 0.5 texture.png
			parseTextureProperty(line, keyword, material) {
				if (!material) return;
				
				// 移除关键字，获取剩余部分
				const textureDef = line.substring(keyword.length).trim();
				
				// 解析纹理参数
				const textureInfo = this.parseTextureDefinition(textureDef);
				
				if (textureInfo) {
					// 存储纹理信息
					material[keyword] = textureInfo;
					
					// 存储参数到textureParams中，便于后续查找
					if (!material.textureParams[keyword]) {
						material.textureParams[keyword] = [];
					}
					material.textureParams[keyword].push(textureInfo);
				}
			}

			// 解析纹理定义（路径和参数）
			parseTextureDefinition(textureDef) {
				const items = textureDef.split(/\\s+/);
				const result = {
					path: '',
					scale: { x: 1, y: 1 },
					offset: { x: 0, y: 0 },
					bumpScale: 1,
					brightness: { base: 0, gain: 1 },
					clamp: false
				};
				
				let i = 0;
				let hasPath = false;
				
				while (i < items.length) {
					const item = items[i];
					
					// 缩放参数: -s <u> <v>
					if (item === '-s' && i + 2 < items.length) {
						result.scale.x = parseFloat(items[i + 1]);
						result.scale.y = parseFloat(items[i + 2]);
						i += 3;
					}
					// 偏移参数: -o <u> <v>
					else if (item === '-o' && i + 2 < items.length) {
						result.offset.x = parseFloat(items[i + 1]);
						result.offset.y = parseFloat(items[i + 2]);
						i += 3;
					}
					// bump缩放参数: -bm <value>
					else if (item === '-bm' && i + 1 < items.length) {
						result.bumpScale = parseFloat(items[i + 1]);
						i += 2;
					}
					// 钳制参数: -clamp on|off
					else if (item === '-clamp' && i + 1 < items.length) {
						result.clamp = items[i + 1].toLowerCase() === 'on';
						i += 2;
					}
					// 亮度参数: -mm <base> <gain>
					else if (item === '-mm' && i + 2 < items.length) {
						result.brightness.base = parseFloat(items[i + 1]);
						result.brightness.gain = parseFloat(items[i + 2]);
						i += 3;
					}
					// 纹理路径（剩余部分）
					else {
						// 将剩余部分组合成路径
						const pathParts = [];
						for (let j = i; j < items.length; j++) {
							if (items[j] && items[j] !== '') {
								pathParts.push(items[j]);
							}
						}
						if (pathParts.length > 0) {
							result.path = PathUtils.cleanTexturePath(pathParts.join(' '));
							hasPath = true;
						}
						break; // 跳出循环，剩余的都是路径
					}
				}
				
				// 如果没有找到路径，尝试将整个字符串作为路径
				if (!hasPath && textureDef.trim()) {
					result.path = PathUtils.cleanTexturePath(textureDef.trim());
				}
				
				return hasPath ? result : null;
			}

			// 获取指定材质的纹理信息
			getTexturesForMaterial(material) {
				const textures = [];
				
				// 检查所有可能的纹理属性
				const textureKeys = ['map_Ka', 'map_Kd', 'map_Ks', 'map_Ke', 
									'map_Ns', 'map_d', 'map_bump', 'bump', 'norm'];
				
				for (const key of textureKeys) {
					if (material[key] && material[key].path) {
						textures.push({
							type: key,
							path: material[key].path,
							params: material[key]
						});
					}
				}
				
				return textures;
			}
		}

		// zip环境贴图读取
		class TextureLoaderFromZip {
			constructor(virtualFS) {
				this.virtualFS = virtualFS;
				this.loadedTextures = new Map();
				this.pendingRequests = new Map();
				
				// 用户可配置的映射规则
				this.mappingRules = [
					// 规则1: 材质名称直接匹配贴图文件名
					(materialName, fileName) => {
						if (!materialName || !fileName) return false;
						const cleanMatName = materialName.toLowerCase().replace(/[^a-z0-9]/g, '');
						const cleanFileName = fileName.toLowerCase().replace(/[^a-z0-9]/g, '');
						return cleanFileName.includes(cleanMatName) || cleanMatName.includes(cleanFileName);
					},
					
					// 规则2: 数字匹配
					(materialName, fileName) => {
						const matNum = (materialName.match(/\d+/) || [])[0];
						const fileNum = (fileName.match(/\d+/) || [])[0];
						return matNum && fileNum && matNum === fileNum;
					},
					
					// 规则3: 常见后缀匹配
					(materialName, fileName, materialIndex) => {
						const suffixes = [
							'_' + (materialIndex + 1),
							(materialIndex + 1),
							'_' + String.fromCharCode(97 + materialIndex),
							String.fromCharCode(97 + materialIndex)
						];
						
						const baseName = fileName.toLowerCase().replace(/\.[^/.]+$/, '');
						return suffixes.some(suffix => baseName.endsWith(suffix) || baseName.includes('_' + suffix + '_'));
					}
				];
				
				// 初始化文件名索引（如果虚拟文件系统没有的话）
				if (virtualFS && !virtualFS.fileNameIndex) {
					virtualFS.fileNameIndex = new Map();
					if (virtualFS.zip) {
						for (const filePath of Object.keys(virtualFS.zip.files)) {
							const fileName = PathUtils.getFileName(filePath);
							if (!virtualFS.fileNameIndex.has(fileName)) {
								virtualFS.fileNameIndex.set(fileName, filePath);
							}
						}
					}
				}
			}

			findTexturePath(texturePath, basePath = null, options = {}) {
				const { textureType = null, materialIndex = 0, totalMaterials = 1 } = options;
				
				// 1. 清洗路径
				const cleanedPath = PathUtils.cleanTextureUrl(texturePath);
				
				// 如果清洗后路径不为空，尝试直接查找
				if (cleanedPath) {
					// 2. 尝试直接查找（使用清洗后的文件名）
					if (this.virtualFS.fileNameIndex && this.virtualFS.fileNameIndex.has(cleanedPath)) {
						const foundPath = this.virtualFS.fileNameIndex.get(cleanedPath);
						return foundPath;
					}
					
					// 3. 尝试相对路径（如果有基础路径）
					if (basePath) {
						const baseDir = basePath.substring(0, basePath.lastIndexOf('/') + 1);
						const relativePath = PathUtils.joinPaths(baseDir, cleanedPath);
						
						if (this.virtualFS.zip && this.virtualFS.zip.file(relativePath)) {
							return relativePath;
						}
					}
					
					// 4. 在ZIP中搜索文件（递归查找）
					if (this.virtualFS.zip) {
						const files = Object.keys(this.virtualFS.zip.files);
						for (const filePath of files) {
							const currentFileName = PathUtils.getFileName(filePath);
							if (currentFileName.toLowerCase() === cleanedPath.toLowerCase()) {
								return filePath;
							}
						}
					}
				}
				
				// 5. 如果以上都没有找到，尝试基于纹理类型和命名模式查找
				return this.findTextureByPattern(texturePath, textureType, materialIndex, totalMaterials);
			}

			findTextureByPattern(texturePath, textureType, materialIndex = 0, totalMaterials = 1, materialName = '') {
				if (!this.virtualFS.zip) {
					return null;
				}
				
				const files = Object.keys(this.virtualFS.zip.files);
				let candidateFiles = [];
				
				// 首先收集所有图片文件
				const imageExtensions = ['.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tiff', '.dds'];
				for (const filePath of files) {
					const ext = filePath.toLowerCase().substring(filePath.lastIndexOf('.'));
					if (imageExtensions.includes(ext)) {
						candidateFiles.push(filePath);
					}
				}
				
				// 如果没有图片文件，返回null
				if (candidateFiles.length === 0) {
					return null;
				}
				
				// ========== 关键策略：基于材质名称和纹理类型精确匹配 ==========
				
				// 策略1: 如果材质名称和贴图文件名有明确的数字对应关系
				if (materialName) {
					// 提取材质名称中的数字
					const materialNumberMatch = materialName.match(/\d+/);
					if (materialNumberMatch) {
						const materialNumber = materialNumberMatch[0];
						
						// 创建可能的贴图文件名模式
						const possiblePatterns = [
							// 直接数字匹配: 53 -> 53.png, texture_53.png, 53_texture.png
							materialNumber,
							// 带材质索引: 53_0, 53_1 等
							materialNumber + '_' + materialIndex,
							// 材质名称的简化版本
							materialName.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase(),
							// 纹理类型结合数字: base_color_53, 53_base_color
							textureType + '_' + materialNumber,
							materialNumber + '_' + textureType
						];
						
						// 尝试匹配每个可能的模式
						for (const pattern of possiblePatterns) {
							for (const filePath of candidateFiles) {
								const fileName = PathUtils.getFileName(filePath).toLowerCase();
								const baseName = fileName.substring(0, fileName.lastIndexOf('.')).toLowerCase();
								
								// 检查是否匹配模式
								if (baseName === pattern || 
									baseName.includes('_' + pattern + '_') || 
									baseName.endsWith('_' + pattern) || 
									baseName.startsWith(pattern + '_')) {
									return filePath;
								}
							}
						}
					}
				}
				
				// 策略2: 基于材质索引的顺序分配（仅在无法精确匹配时使用）
				if (candidateFiles.length === totalMaterials && totalMaterials > 1) {
					// 如果贴图数量和材质数量相同，按顺序分配
					const selectedFile = candidateFiles[materialIndex % candidateFiles.length];
					return selectedFile;
				}
				
				// 策略3: 如果以上都失败，返回第一个贴图文件
				return candidateFiles[0];
			}

			async loadTextures(textureRequests, basePath = null) {
				const results = [];
				for (const request of textureRequests) {
					try {
						const options = request.options || {};
						if (basePath && !options.basePath) {
							options.basePath = basePath;
						}
						
						const texture = await this.loadTexture(request.path, options);
						results.push({
							...request,
							texture: texture,
							path: request.path,
							options: options
						});
					} catch (error) {
						console.log('Load Textures failed:', request.path, error);
						results.push({
							...request,
							texture: null,
							error: error
						});
					}
				}
				
				return results;
			}

			async loadTexture(texturePath, options = {}) {
				const { basePath = null, textureType = null, materialIndex = 0, totalMaterials = 1 } = 
					typeof options === 'string' ? { basePath: options } : options;
				
				// 查找实际路径
				const actualPath = this.findTexturePath(texturePath, basePath, {
					textureType,
					materialIndex,
					totalMaterials
				});
				
				if (!actualPath) {
					throw new Error('Texture not found: ' + texturePath);
				}
				
				// 检查是否已经加载
				if (this.loadedTextures.has(actualPath)) {
					return this.loadedTextures.get(actualPath);
				}
				
				// 检查是否有正在进行的请求
				if (this.pendingRequests.has(actualPath)) {
					return await this.pendingRequests.get(actualPath);
				}
				
				// 创建新的加载请求
				const loadPromise = (async () => {
					try {
						// 从虚拟文件系统获取blob URL
						const blobUrl = await this.virtualFS.getBlobUrl(actualPath, basePath);
						
						// 加载纹理
						const texture = await new Promise((resolve, reject) => {
							const loader = new THREE.TextureLoader();
							loader.load(
								blobUrl,
								(loadedTexture) => {
									// 设置默认包装方式
									loadedTexture.wrapS = THREE.RepeatWrapping;
									loadedTexture.wrapT = THREE.RepeatWrapping;
									
									// 根据纹理类型设置色彩空间
									if (textureType === 'base_color' || textureType === 'emissive' || textureType === 'map') {
										loadedTexture.colorSpace = THREE.SRGBColorSpace;
									} else {
										loadedTexture.colorSpace = THREE.LinearSRGBColorSpace;
									}
									
									// 记录材质索引信息
									loadedTexture.userData = loadedTexture.userData || {};
									loadedTexture.userData.materialIndex = materialIndex;
									loadedTexture.userData.originalPath = actualPath;
									
									// 缓存纹理
									this.loadedTextures.set(actualPath, loadedTexture);
									resolve(loadedTexture);
								},
								undefined,
								(error) => {
									console.log('Load Texture failed:', actualPath, error);
									reject(error);
								}
							);
						});
						
						return texture;
					} catch (error) {
						console.log('Load Texture failed:', actualPath, error);
						throw error;
					} finally {
						// 清理pending请求
						this.pendingRequests.delete(actualPath);
					}
				})();
				
				// 保存pending请求
				this.pendingRequests.set(actualPath, loadPromise);
				
				return loadPromise;
			}

			dispose() {
				this.loadedTextures.forEach(texture => {
					if (texture.image && texture.image.src && texture.image.src.startsWith('blob:')) {
						URL.revokeObjectURL(texture.image.src);
					}
				});
				this.loadedTextures.clear();
				this.pendingRequests.clear();
			}
		}

		// 主函数
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
					
					controlsDisabled: false,
					isMouseDown: false,
					mouseDownTime: 0,
					
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
							emissive: '#000000',
							emissiveIntensity: 0.0,
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
							thickness: 1.0,
							depthThreshold: 0.015,
							normalThreshold: 0.4
						}
					},
					postProcessingParams: {
						ssao: {
							kernelRadius: 16,
							minDistance: 0.001,
							maxDistance: 0.5,
							output: SSAOPass.OUTPUT.Blur
						},
						gtao: {
							radius: 0.25,
							distanceExponent: 1.0,
							thickness: 1.0,
							scale: 1.0,
							distanceFallOff: 1.0,
							samples: 16,
							denoiseRadius: 4.0,
							lumaPhi: 10.0,
							depthPhi: 2.0,
							normalPhi: 3.0,
							output: GTAOPass.OUTPUT.Denoise
						}
					},
					commonParams: {
						side: 'Front',
						background: '#111111'
					},
					
					useVertexColors: false,
					textureMapping: true,
					originalTextures: new Map(),
					textureCache: new Map(),
					
					playback: {
						maxFPS: 90,
						sPlaying: false,
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
					selectedMaterialGUI: {
						visible: false,
						guiInstance: null,
						container: null,
						title: '',
						material: null,
						object: null,
						isMultiMaterial: false,
						materialIndex: 0,
						materialArray: null
					},
					lightGUI: {
						visible: false,
						guiInstance: null,
						container: null,
						dirLightFolder: null,
						ambLightFolder: null
					},
					
					selection: {
						selectedObject: null,
						selectionBBox: null,
						selectionHelper: null,
						raycaster: new THREE.Raycaster(),
						mouse: new THREE.Vector2(),
						isSelecting: false
					},
					
					getScene3DData: {
						isProcessing: false,
						screenshotQueue: []
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
				this.loadingProgress = new LoadingProgressManager(this);
				this.textureManager = new TextureManager(this);
				this.renderer = null;
				this.composer = null;
				this.contourPass = null;
				this.normalRenderTarget = null;
				this.depthTexture = null;
				this.isContourMode = false;
				this._rafId = null;
				this.needsRender = true;
				this.isLoopRunning = false;
				
				this.camera = null;
				this.controls = null;
				this.materialConversionCache = new Map();
				
				this.scene = null;
				this.JSZip = JSZip;
				this.currentVirtualFS = null;
				this.currentZipMainFile = null;
				this.textureLoader = null;
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
					container: get('canvas-container'),
					controlsPanel: get('controls'),
					loading: get('loading'),
					loadingText: get('loading-text'),
					loadingSpinner: get('loading-spinner'),
					loadingProgressBar: get('loading-progress-bar'),
					loadingPercentage: get('loading-percentage'),
					infoDisplay: get('info-display'),
					
					labels: {
						bgColorLabel: get('bg-color-label'),
						lightLabel: get('light-mode-label'),
						
						keyCount: get('keyframe-count'),
						ortho: document.querySelector('.fixed-width-label-ortho'),
						fov: get('fov-label'),
						clip: document.querySelector('.fixed-width-label-clip'),
						roll: document.querySelector('.fixed-width-label-roll')
					},
					btns: {
						import: get('import-btn'),
						export: get('export-btn'),
						diagnostic: get('diagnostic-btn'),
						clear: get('clear-btn'),
						focusLight: get('focus-light'),
						resetSettings: get('reset-settings'),
						
						first: get('first-frame'),
						prevKey: get('prev-keyframe'),
						prevFrame: get('prev-frame'),
						reverse: get('reverse-play'),
						play: get('play-btn'),
						nextFrame: get('next-frame'),
						nextKey: get('next-keyframe'),
						last: get('last-frame'),
						toggleCamAnim: get('toggle-camera-anim'),
						sceneLength: get('scene-length-btn'),
						screenshot: get('screenshot-btn'),
						record: get('record-btn'),
						threedDataBtn: get('threed-data-btn'),
						
						newCamera: get('new-camera-btn'),
						centerToObject: get('center-to-object-btn'), 
						focusToObject: get('focus-to-object-btn'),
						autoKeyframe: get('auto-keyframe'),
						addCamKey: get('add-keyframe'),
						delCamKey: get('delete-keyframe'),
						clearCamKey: get('clear-keyframes'), 
						deleteCustomCamera: get('delete-custom-camera'),
						resetCamera: get('reset-camera'),
						yup: get('y-up-btn')
					},
					inputs: {
						file: get('import-file-input'),
						materialSelect: get('material-mode-select'),
						bgColorPicker: get('bg-color-picker'),
						sideSelect: get('side-select'),
						helperSize: get('helper-size-slider'),
						
						fps: get('fps-input'),
						slider: get('slider'),
						startFrame: get('start-frame'),
						endFrame: get('end-frame'),
						
						views: get('views-select'),
						fov: get('fov-input'),
						near: get('near-input'),
						far: get('far-input'),
						rollAngle: get('roll-angle')
					},
					toggles: {
						info: get('info-display-toggle'),
						helper: get('helper-toggle'),
						light: get('light-mode-toggle'),
						shadows: get('shadows-toggle'),
						ortho: get('orthographic-toggle')
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
				// BasicShadowMap | PCFSoftShadowMap | VSMShadowMap
				this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
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
				
				this.initializeMaterialAndLightModes();
				
				this.initMaterialGUI();
				this.initLightGUI();
				this.dom.loading.style.display = 'none';
				
				this.dom.inputs.sideSelect.value = this.state.commonParams.side;
				
				this.updateBgColorPickerState(this.state.materialMode);
				this.handleScrollDragging();
				this.updateTimeSleder();
				this.updateKeyframeButtonsState();
				this.updateAutoAddKeyframeButtonState();
				this.updateInfoDisplay();
				this.updateViewsMenu();
				this.updateCameraUIForMode();
				
				this.bindEvents();
				this.renderOnce();
			}

			bindEvents() {
				const b = this.dom.btns, i = this.dom.inputs, t = this.dom.toggles;
				
				b.import.onclick = () => i.file.click();
				i.file.onchange = (e) => this.handleImportFile(e);
				b.export.onclick = () => this.exportModel();
				b.diagnostic.onclick = () => this.sceneDiagnostics();
				b.clear.onclick = () => this.clearScene();
				t.info.onchange = () => this.toggleInfoDisplay();
				t.helper.onchange = () => this.toggleHelper();
				i.materialSelect.onchange = (e) => this.handleMatChange(e);
				i.bgColorPicker.oninput = () => this.updateSceneBackground();
				i.sideSelect.onchange = (e) => this.updateMaterialSide(e);
				t.light.onchange = () => this.toggleLightMode();
				t.shadows.onchange = () => this.toggleShadows();
				b.focusLight.onclick= () => this.adjustDefaultDirLightForScene();
				b.resetSettings.onclick = () => this.resetSettings();
				i.helperSize.oninput = () => this.updateHelperSize();
				
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
				b.screenshot.onclick = () => this.captureScreenshot();
				b.record.onclick = () => this.startRecording();
				b.threedDataBtn.onclick = () => this.getScene3DData();
				
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
				
				// FOV/Size 输入
				i.fov.oninput = (e) => {
					this.validateNumericInput(e, 'fov');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.fov.onkeydown = (e) => {
					if (e.key === 'Enter') {
						this.applyNumericInput(e, 'fov', true);
					}
				};
				i.fov.onblur = (e) => {
					this.applyNumericInput(e, 'fov', true);
				}
				
				// Near 输入
				i.near.oninput = (e) => {
					this.validateNumericInput(e, 'near');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.near.onkeydown = (e) => {
					if (e.key === 'Enter') {
						this.applyNumericInput(e, 'near');
					}
				};
				i.near.onblur = (e) => {
					this.applyNumericInput(e, 'near');
				}
				
				// Far 输入
				i.far.oninput = (e) => {
					this.validateNumericInput(e, 'far');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.far.onkeydown = (e) => {
					if (e.key === 'Enter') {
						this.applyNumericInput(e, 'far');
					}
				};
				i.far.onblur = (e) => {
					this.applyNumericInput(e, 'far');
				}
				
				// Roll angle 输入
				i.rollAngle.oninput = (e) => {
					this.validateNumericInput(e, 'roll');
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
				};
				i.rollAngle.onkeydown = (e) => {
					if (e.key === 'Enter') {
						this.applyNumericInput(e, 'roll', true);
					}
				};
				i.rollAngle.onblur = (e) => {
					this.applyNumericInput(e, 'roll', true);
				}
				
				// OrbitControls 事件
				this.controls.addEventListener('end', () => {
					if (this.state.autoAddKeyframeEnabled && this.state.cameras.currentType === 'custom') {
						this.addCameraKeyframe();
					}
				});
				this.controls.addEventListener('change', () => {
					if (!this.state.cameraAnim.isEnabled) {
						this.saveCurrentCameraState();
					}
					this.renderInvalidate();
				});
				this.renderer.domElement.addEventListener('wheel', (e) => {
					this.handleCameraWheel(e), {
						passive: false
					}
				});
				
				// 鼠标选择
				this.renderer.domElement.addEventListener('mousedown', (e) => {
					this.state.isMouseDown = true;
					this.state.mouseDownTime = Date.now();
				});
				
				this.renderer.domElement.addEventListener('mouseup', (e) => {
					if (!this.state.isMouseDown) return;
					
					const clickDuration = Date.now() - this.state.mouseDownTime;
					this.state.isMouseDown = false;
					
					// 如果点击持续时间小于200ms且没有明显移动，认为是单击（选择操作）
					if (clickDuration < 200) {
						this.handleCanvasClick(e);
					}
					// 否则是拖拽操作（旋转视窗），不改变选择状态
				});
				
				// 窗口变化事件
				window.addEventListener('resize', this.debounce(() => {
					this.onWindowResize(), 100
				}));
				
				// ComfyUI界面file_path监听
				window.addEventListener('message', (e) => {
					this.handleImportMessage(e)
				});
			}

			// 核心控制
			handleCanvasClick(event) {
				if (this.state.controlsDisabled || !this.state.currentModel) return;
				
				// 防止在旋转视窗时改变选择状态
				if (this.state.isMouseDown && (Date.now() - this.state.mouseDownTime) >= 200) {
					return;
				}
				
				const rect = this.renderer.domElement.getBoundingClientRect();
				this.state.selection.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
				this.state.selection.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
				
				this.state.selection.raycaster.setFromCamera(this.state.selection.mouse, this.camera);
				
				const intersects = this.state.selection.raycaster.intersectObject(this.scene, true);
				
				// 过滤出Mesh对象
				const meshIntersects = intersects.filter(intersect => intersect.object.isMesh);
				
				if (meshIntersects.length > 0) {
					const selectedObject = meshIntersects[0].object;
					this.selectObject(selectedObject);
				} else {
					this.clearSelection();
				}
				
				this.renderInvalidate();
			}

			selectObject(object) {
				// 清除之前的选择
				this.clearSelection();
				
				// 保存选中的对象
				this.state.selection.selectedObject = object;
				this.state.selection.isSelecting = true;
				
				// 创建BoundingBox辅助线
				const bbox = new THREE.Box3().setFromObject(object);
				const bboxHelper = new THREE.Box3Helper(bbox, 0xffff00);
				bboxHelper.name = "SelectionBBox";
				this.scene.add(bboxHelper);
				this.state.selection.selectionBBox = bboxHelper;
				
				// 创建选择辅助对象（用于可视化）
				const geometry = new THREE.BoxGeometry(1, 1, 1);
				const edges = new THREE.EdgesGeometry(geometry);
				const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ 
					color: 0xffff00, 
					linewidth: 2 
				}));
				
				// 缩放线框到物体大小
				const size = new THREE.Vector3();
				bbox.getSize(size);
				line.scale.copy(size);
				
				// 定位到物体中心
				const center = new THREE.Vector3();
				bbox.getCenter(center);
				line.position.copy(center);
				
				line.name = "SelectionHelper";
				this.scene.add(line);
				this.state.selection.selectionHelper = line;
				
				// 如果是original材质模式，显示材质GUI
				if (this.state.materialMode === 'original' && object.material) {
					this.showSelectedMaterialGUI(object);
				}
				
				this.updateInfoDisplay();
			}

			clearSelection() {
				// 移除BBox辅助线
				if (this.state.selection.selectionBBox) {
					this.scene.remove(this.state.selection.selectionBBox);
					this.state.selection.selectionBBox.geometry.dispose();
					this.state.selection.selectionBBox.material.dispose();
					this.state.selection.selectionBBox = null;
				}
				
				// 移除选择辅助对象
				if (this.state.selection.selectionHelper) {
					this.scene.remove(this.state.selection.selectionHelper);
					this.state.selection.selectionHelper.geometry.dispose();
					this.state.selection.selectionHelper.material.dispose();
					this.state.selection.selectionHelper = null;
				}
				
				// 清除选择状态
				this.state.selection.selectedObject = null;
				this.state.selection.isSelecting = false;
				
				// 隐藏材质GUI（不销毁材质引用）
				this.hideSelectedMaterialGUI();
				
				// 清除材质引用（只在清除选择时）
				this.state.selectedMaterialGUI.material = null;
				this.state.selectedMaterialGUI.object = null;
				this.state.selectedMaterialGUI.title = '';
				this.state.selectedMaterialGUI.isMultiMaterial = false;
				this.state.selectedMaterialGUI.materialIndex = 0;
				this.state.selectedMaterialGUI.materialArray = null;
				
				this.updateInfoDisplay();
			}

			updateSelectionHelpers() {
				if (!this.state.selection.selectedObject || !this.state.selection.selectionBBox) return;
				
				const bbox = new THREE.Box3().setFromObject(this.state.selection.selectedObject);
				
				// 更新BBox
				this.state.selection.selectionBBox.box = bbox;
				
				// 更新线框辅助
				if (this.state.selection.selectionHelper) {
					const size = new THREE.Vector3();
					bbox.getSize(size);
					this.state.selection.selectionHelper.scale.copy(size);
					
					const center = new THREE.Vector3();
					bbox.getCenter(center);
					this.state.selection.selectionHelper.position.copy(center);
				}
			}

			handleScrollDragging() {
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
				
				this.renderInvalidate();
			}

			showMessage(message, duration = 3000) {
				this.dom.loadingText.textContent = message;
				this.dom.loading.style.display = 'block';
				
				if (this._messageTimer) {
					clearTimeout(this._messageTimer);
				}
				
				if (duration > 0) {
					this._messageTimer = setTimeout(() => {
						if (!this.state.loading) {
							this.dom.loading.style.display = 'none';
						}
					}, duration);
				}
			}

			updateLoadingProgress(percentage, message = null) {
				const clampedPercentage = Math.max(0, Math.min(100, percentage));
				
				if (message) {
					this.dom.loadingText.textContent = message;
				}
				
				this.dom.loadingProgressBar.style.width = clampedPercentage + '%';
				this.dom.loadingPercentage.textContent = Math.round(clampedPercentage) + '%';
				
				// 如果进度达到100%，准备隐藏加载指示器
				if (clampedPercentage >= 100) {
					setTimeout(() => {
						if (!this.state.loading && !this._messageTimer) {
							this.dom.loading.style.display = 'none';
						}
					}, 500);
				}
			}

			disableControls() {
				this.state.controlsDisabled = true;
				
				// 禁用控制面板
				this.dom.controlsPanel.classList.add('controls-disabled');
				
				// 禁用所有按钮和输入控件
				const allInteractiveElements = this.dom.controlsPanel.querySelectorAll('button, input, select, label');
				allInteractiveElements.forEach(el => {
					// 保存原始背景色（如果有内联样式）
					if (el.style.background && !el.getAttribute('data-original-bg')) {
						el.setAttribute('data-original-bg', el.style.background);
					}
					
					// 清除内联背景色，让CSS类生效
					el.style.background = '';
					
					el.disabled = true;
					el.classList.add('disabled-control');
				});
				
				// 隐藏GUI
				this.hideMaterialGUI();
				this.hideLightGUI();
				
				// 隐藏GUI容器
				if (this.state.materialGUI.container) {
					this.state.materialGUI.container.classList.add('material-gui-disabled');
				}
				if (this.state.lightGUI.container) {
					this.state.lightGUI.container.classList.add('light-gui-disabled');
				}
				
				this.updateKeyframeButtonsState();
				this.updateCameraUIForMode();
				this.updateCameraControlsState();
				this.updateOrthoToggleState();
			}

			enableControls() {
				this.state.controlsDisabled = false;
				
				// 启用控制面板
				this.dom.controlsPanel.classList.remove('controls-disabled');
				
				// 启用所有按钮和输入控件（除了本来就禁用的）
				const allInteractiveElements = this.dom.controlsPanel.querySelectorAll('button, input, select, label');
				allInteractiveElements.forEach(el => {
					// 只启用那些不是固有禁用的元素
					if (!el.hasAttribute('data-inherently-disabled')) {
						el.disabled = false;
						el.classList.remove('disabled-control');
						
						// 恢复原始背景色
						const originalBg = el.getAttribute('data-original-bg');
						if (originalBg) {
							el.style.background = originalBg;
							el.removeAttribute('data-original-bg');
						}
					}
				});
				
				// 恢复GUI容器显示
				if (this.state.materialGUI.container) {
					this.state.materialGUI.container.classList.remove('material-gui-disabled');
				}
				if (this.state.lightGUI.container) {
					this.state.lightGUI.container.classList.remove('light-gui-disabled');
				}
				
				// 重新应用按钮状态
				this.updateKeyframeButtonsState();
				this.updateCameraUIForMode();
				this.updateCameraControlsState();
				this.updateOrthoToggleState();
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
				
				// 添加选择信息
				if (this.state.selection.isSelecting && this.state.selection.selectedObject) {
					const selectedName = this.state.selection.selectedObject.name || 'Unnamed Mesh';
					info += ' | Selected: ' + selectedName;
				}
				
				// 添加FPS信息
				/* if (this.fps && this.fps.value > 0) {
					info += ' | ' + this.fps.value + ' FPS';
				} else {
					info += ' | 0 FPS';
				} */
				
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

			toggleHelper() {
				const vis = this.dom.toggles.helper.checked;
				if(this.state.grid) this.state.grid.visible = vis;
				if(this.state.axesHelper) this.state.axesHelper.visible = vis;
				this.updateVisualizationVisibility();
				this.renderInvalidate();
			}

			updateHelperSize() {
				const slider = this.dom.inputs.helperSize;
				if (!slider) return;
				
				const value = parseFloat(slider.value);
				this.state.helperSize = value;
				
				this.updateAllVisualizationSizes();
				this.renderInvalidate();
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
				// 调整角度确保最短路径
				const adjustForShortestPath = (angles) => {
				for (let i = 1; i < angles.length; i++) {
					const prev = angles[i-1];
					const curr = angles[i];
					
					// 计算差值，找到最短路径
					let diff = curr - prev;
					
					// 如果差值大于π，减去2π
					if (diff > Math.PI) {
						angles[i] -= 2 * Math.PI;
					}
					// 如果差值小于-π，加上2π
					else if (diff < -Math.PI) {
						angles[i] += 2 * Math.PI;
					}
				}
				
				// 确保e0与e1保持一致（因为e0在e1之前）
				if (angles.length > 1) {
					let diff = angles[1] - angles[0];
					if (diff > Math.PI) {
						angles[0] -= 2 * Math.PI;
					} else if (diff < -Math.PI) {
						angles[0] += 2 * Math.PI;
					}
				}
				
				// 确保e3与e2保持一致（因为e3在e2之后）
				if (angles.length > 3) {
					let diff = angles[3] - angles[2];
					if (diff > Math.PI) {
						angles[3] -= 2 * Math.PI;
					} else if (diff < -Math.PI) {
						angles[3] += 2 * Math.PI;
					}
				}
				
				return angles;
				};
				
				var interpolateAngle = function(t, a0, a1, a2, a3) {
					var normalizeAngle = function(angle) {
						while (angle > Math.PI) angle -= 2 * Math.PI;
						while (angle < -Math.PI) angle += 2 * Math.PI;
						return angle;
					};
					
					a0 = normalizeAngle(a0);
					a1 = normalizeAngle(a1);
					a2 = normalizeAngle(a2);
					a3 = normalizeAngle(a3);
					
					// 调整角度确保插值沿最短路径
					const adjusted = adjustForShortestPath([a0, a1, a2, a3]);
					a0 = adjusted[0];
					a1 = adjusted[1];
					a2 = adjusted[2];
					a3 = adjusted[3];
					
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
					console.log('Error creating GUI:', error);
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
					} catch (e) {}
					this.state.materialGUI.defaultFolder = null;
				}
				
				this.state.materialGUI.defaultFolder = this.state.materialGUI.guiInstance.addFolder('Default Material');
				
				const controllers = {};
				
				controllers.color = this.state.materialGUI.defaultFolder.addColor(this.state.materialParams.default, 'color')
					.onChange((value) => {
						this.state.materialParams.default.color = value;
						this.updateDefaultMaterial();
					}).name('Color');
				
				controllers.roughness = this.state.materialGUI.defaultFolder.add(this.state.materialParams.default, 'roughness', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.default.roughness = value;
						this.updateDefaultMaterial();
					}).name('Roughness');
				
				controllers.metalness = this.state.materialGUI.defaultFolder.add(this.state.materialParams.default, 'metalness', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.default.metalness = value;
						this.updateDefaultMaterial();
					}).name('Metalness');
				
				controllers.flatShading = this.state.materialGUI.defaultFolder.add(this.state.materialParams.default, 'flatShading')
					.onChange((value) => {
						this.state.materialParams.default.flatShading = value;
						this.updateDefaultMaterial();
					}).name('Flat Shading');
				
				this.state.materialGUI.defaultFolder.add({
					reset: () => this.resetDefaultParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.defaultControllers = controllers;
				this.state.materialGUI.defaultFolder.open();
			}

			createWireframeMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.wireframeFolder) {
					try {
						this.state.materialGUI.wireframeFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.wireframeFolder = null;
				}
				
				this.state.materialGUI.wireframeFolder = this.state.materialGUI.guiInstance.addFolder('Wireframe Material');
				
				const controllers = {};
				
				controllers.color = this.state.materialGUI.wireframeFolder.addColor(this.state.materialParams.wireframe, 'color')
					.onChange((value) => {
						this.state.materialParams.wireframe.color = value;
						this.updateWireframeMaterial();
					}).name('Wireframe Color');
				
				controllers.linewidth = this.state.materialGUI.wireframeFolder.add(this.state.materialParams.wireframe, 'linewidth', 0.1, 5, 0.1)
					.onChange((value) => {
						this.state.materialParams.wireframe.linewidth = value;
						this.updateWireframeMaterial();
					}).name('Line Width');
				
				controllers.opacity = this.state.materialGUI.wireframeFolder.add(this.state.materialParams.wireframe, 'opacity', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.wireframe.opacity = value;
						this.updateWireframeMaterial();
					}).name('Opacity');
				
				this.state.materialGUI.wireframeFolder.add({
					reset: () => this.resetWireframeParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.wireframeControllers = controllers;
				this.state.materialGUI.wireframeFolder.open();
			}

			createNormalMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.normalFolder) {
					try {
						this.state.materialGUI.normalFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.normalFolder = null;
				}
				
				this.state.materialGUI.normalFolder = this.state.materialGUI.guiInstance.addFolder('Normal Material');
				
				const controllers = {};
				
				controllers.flatShading = this.state.materialGUI.normalFolder.add(this.state.materialParams.normal, 'flatShading')
					.onChange((value) => {
						this.state.materialParams.normal.flatShading = value;
						this.updateNormalMaterial();
					}).name('Flat Shading');
				
				this.state.materialGUI.normalFolder.add({
					reset: () => this.resetNormalParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.normalControllers = controllers;
				this.state.materialGUI.normalFolder.open();
			}

			createLineArtMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.lineartFolder) {
					try {
						this.state.materialGUI.lineartFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.lineartFolder = null;
				}
				
				this.state.materialGUI.lineartFolder = this.state.materialGUI.guiInstance.addFolder('Lineart Material');
				
				const controllers = {};
				
				controllers.color = this.state.materialGUI.lineartFolder.addColor(this.state.materialParams.lineart, 'color')
					.onChange((value) => {
						this.state.materialParams.lineart.color = value;
						this.updateLineartMaterial();
					}).name('Color');
				
				controllers.edgeStart = this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'edgeStart', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.edgeStart = value;
						this.updateLineartMaterial();
					}).name('Edge Start');
				
				controllers.edgeEnd = this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'edgeEnd', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.edgeEnd = value;
						this.updateLineartMaterial();
					}).name('Edge End');
				
				controllers.curvatureStart = this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'curvatureStart', 0, 0.1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.curvatureStart = value;
						this.updateLineartMaterial();
					}).name('Curvature Start');
				
				controllers.curvatureEnd = this.state.materialGUI.lineartFolder.add(this.state.materialParams.lineart, 'curvatureEnd', 0, 0.1, 0.01)
					.onChange((value) => {
						this.state.materialParams.lineart.curvatureEnd = value;
						this.updateLineartMaterial();
					}).name('Curvature End');
				
				this.state.materialGUI.lineartFolder.add({
					reset: () => this.resetLineartParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.lineartControllers = controllers;
				this.state.materialGUI.lineartFolder.open();
			}

			createCannyMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.cannyFolder) {
					try {
						this.state.materialGUI.cannyFolder.destroy();
					} catch(e) {}
					this.state.materialGUI.cannyFolder = null;
				}
				
				this.state.materialGUI.cannyFolder = this.state.materialGUI.guiInstance.addFolder('Canny Material');
				const controllers = {};
				
				controllers.color = this.state.materialGUI.cannyFolder.addColor(this.state.materialParams.canny, 'color')
					.onChange((value) => {
						this.state.materialParams.canny.color = value;
						this.updateCannyMaterial();
					}).name('Color');
				
				controllers.lowThreshold = this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'lowThreshold', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.lowThreshold = value;
						this.updateCannyMaterial();
					}).name('Low Threshold');
				
				controllers.highThreshold = this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'highThreshold', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.highThreshold = value;
						this.updateCannyMaterial();
					}).name('High Threshold');
				
				controllers.edgeStrength = this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'edgeStrength', 0, 5, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.edgeStrength = value;
						this.updateCannyMaterial();
					}).name('Edge Strength');
				
				controllers.edgeDetail = this.state.materialGUI.cannyFolder.add(this.state.materialParams.canny, 'edgeDetail', 0.1, 0.9, 0.01)
					.onChange((value) => {
						this.state.materialParams.canny.edgeDetail = value;
						this.updateCannyMaterial();
					}).name('Edge Detail');
				
				this.state.materialGUI.cannyFolder.add({
					reset: () => this.resetCannyParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.cannyControllers = controllers;
				this.state.materialGUI.cannyFolder.open();
			}

			createEdgeMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.edgeFolder) {
					try {
						this.state.materialGUI.edgeFolder.destroy();
					} catch(e) {}
					this.state.materialGUI.edgeFolder = null;
				}
				
				this.state.materialGUI.edgeFolder = this.state.materialGUI.guiInstance.addFolder('Edge Material');
				
				const controllers = {};
				
				controllers.color = this.state.materialGUI.edgeFolder.addColor(this.state.materialParams.edge, 'color')
					.onChange((value) => {
						this.state.materialParams.edge.color = value;
						this.updateEdgeMaterial();
					}).name('Color');
				
				controllers.normalThreshold = this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'normalThreshold', 0, 10, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.normalThreshold = value;
						this.updateEdgeMaterial();
					}).name('Normal Threshold');
				
				controllers.posThreshold = this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'posThreshold', 0, 10, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.posThreshold = value;
						this.updateEdgeMaterial();
					}).name('Position Threshold');
				
				controllers.edgeStart = this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'edgeStart', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.edgeStart = value;
						this.updateEdgeMaterial();
					}).name('Edge Start');
				
				controllers.edgeEnd = this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'edgeEnd', 0, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.edgeEnd = value;
						this.updateEdgeMaterial();
					}).name('Edge End');
				
				controllers.contrast = this.state.materialGUI.edgeFolder.add(this.state.materialParams.edge, 'contrast', 1, 2, 0.01)
					.onChange((value) => {
						this.state.materialParams.edge.contrast = value;
						this.updateEdgeMaterial();
					}).name('Contrast');
				
				this.state.materialGUI.edgeFolder.add({
					reset: () => this.resetEdgeParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.edgeControllers = controllers;
				this.state.materialGUI.edgeFolder.open();
			}

			createContourMaterialFolder() {
				if (!this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.contourFolder) {
					try {
						this.state.materialGUI.contourFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.contourFolder = null;
				}
				
				this.state.materialGUI.contourFolder = this.state.materialGUI.guiInstance.addFolder('Contour Material');
				
				const controllers = {};
				
				controllers.color = this.state.materialGUI.contourFolder.addColor(this.state.materialParams.contour, 'color')
					.onChange((value) => {
						this.state.materialParams.contour.color = value;
						this.updateContourMaterial();
					}).name('Color');
				
				controllers.thickness = this.state.materialGUI.contourFolder.add(this.state.materialParams.contour, 'thickness', 0.1, 10, 0.01)
					.onChange((value) => {
						this.state.materialParams.contour.thickness = value;
						this.updateContourMaterial();
					}).name('Thickness');
				
				controllers.depthThreshold = this.state.materialGUI.contourFolder.add(this.state.materialParams.contour, 'depthThreshold', 0.01, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.contour.depthThreshold = value;
						this.updateContourMaterial();
					}).name('Depth Threshold');
				
				controllers.normalThreshold = this.state.materialGUI.contourFolder.add(this.state.materialParams.contour, 'normalThreshold', 0.01, 1, 0.01)
					.onChange((value) => {
						this.state.materialParams.contour.normalThreshold = value;
						this.updateContourMaterial();
					}).name('Normal Threshold');
				
				this.state.materialGUI.contourFolder.add({
					reset: () => this.resetContourParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.contourControllers = controllers;
				this.state.materialGUI.contourFolder.open();
			}

			createSSAOGUIFolder() {
				if (!this.ssaoPass || !this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.ssaoFolder) {
					try {
						this.state.materialGUI.ssaoFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.ssaoFolder = null;
				}
				
				this.state.materialGUI.ssaoFolder = this.state.materialGUI.guiInstance.addFolder('SSAO Settings');
				
				const ssaoParams = this.state.postProcessingParams.ssao;
				const controllers = {};
				
				controllers.kernelRadius = this.state.materialGUI.ssaoFolder.add(ssaoParams, 'kernelRadius', 0, 32, 0.5)
					.onChange((value) => {
						ssaoParams.kernelRadius = value;
						this.updateSSAOParameters();
					}).name('Kernel Radius');
				
				controllers.minDistance = this.state.materialGUI.ssaoFolder.add(ssaoParams, 'minDistance', 0.001, 1, 0.001)
					.onChange((value) => {
						ssaoParams.minDistance = value;
						this.updateSSAOParameters();
					}).name('Min Distance');
				
				controllers.maxDistance = this.state.materialGUI.ssaoFolder.add(ssaoParams, 'maxDistance', 0.001, 1, 0.001)
					.onChange((value) => {
						ssaoParams.maxDistance = value;
						this.updateSSAOParameters();
					}).name('Max Distance');
				
				this.state.materialGUI.ssaoFolder.add({
					reset: () => this.resetSSAOParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.ssaoControllers = controllers;
				this.state.materialGUI.ssaoFolder.open();
			}

			createGTAOGUIFolder() {
				if (!this.gtaoPass || !this.state.materialGUI.guiInstance) return;
				
				if (this.state.materialGUI.gtaoFolder) {
					try {
						this.state.materialGUI.gtaoFolder.destroy();
					} catch (e) {}
					this.state.materialGUI.gtaoFolder = null;
				}
				
				this.state.materialGUI.gtaoFolder = this.state.materialGUI.guiInstance.addFolder('GTAO Settings');
				
				const gtaoParams = this.state.postProcessingParams.gtao;
				const controllers = {};
				
				controllers.radius = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'radius', 0.01, 1, 0.01)
					.onChange((value) => {
						gtaoParams.radius = value;
						this.UpdateGTAOParameters();
					}).name('Radius');
				
				controllers.distanceExponent = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'distanceExponent', 1, 4, 0.1)
					.onChange((value) => {
						gtaoParams.distanceExponent = value;
						this.UpdateGTAOParameters();
					}).name('Distance Exponent');
				
				controllers.thickness = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'thickness', 0.01, 10, 0.01)
					.onChange((value) => {
						gtaoParams.thickness = value;
						this.UpdateGTAOParameters();
					}).name('Thickness');
				
				controllers.scale = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'scale', 0.01, 2.0, 0.01)
					.onChange((value) => {
						gtaoParams.scale = value;
						this.UpdateGTAOParameters();
					}).name('Scale');
				
				controllers.distanceFallOff = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'distanceFallOff', 0, 1, 0.01)
					.onChange((value) => {
						gtaoParams.distanceFallOff = value;
						this.UpdateGTAOParameters();
					}).name('Distance Falloff');
				
				controllers.samples = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'samples', 2, 32, 1)
					.onChange((value) => {
						gtaoParams.samples = value;
						this.UpdateGTAOParameters();
					}).name('Samples');
				
				controllers.denoiseRadius = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'denoiseRadius', 1, 8, 0.01)
					.onChange((value) => {
						gtaoParams.denoiseRadius = value;
						this.UpdateGTAOParameters();
					}).name('Denoise');
				/* 
				controllers.lumaPhi = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'lumaPhi', 1, 20, 1)
					.onChange((value) => {
						gtaoParams.lumaPhi = value;
						this.UpdateGTAOParameters();
					}).name('luma Phi');
				
				controllers.depthPhi = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'depthPhi', 0.5, 5, 0.01)
					.onChange((value) => {
						gtaoParams.depthPhi = value;
						this.UpdateGTAOParameters();
					}).name('depth Phi');
				
				controllers.normalPhi = this.state.materialGUI.gtaoFolder.add(gtaoParams, 'normalPhi', 0.5, 5, 0.01)
					.onChange((value) => {
						gtaoParams.normalPhi = value;
						this.UpdateGTAOParameters();
					}).name('normal Phi');
				*/
				this.state.materialGUI.gtaoFolder.add({
					reset: () => this.resetGTAOParameters()
				}, 'reset').name('Reset');
				
				this.state.materialGUI.gtaoControllers = controllers;
				this.state.materialGUI.gtaoFolder.open();
			}

			// 选择材质GUI
			initSelectedMaterialGUI() {
				// 创建GUI容器
				this.state.selectedMaterialGUI.container = document.createElement('div');
				this.state.selectedMaterialGUI.container.id = 'selected-material-gui';
				this.state.selectedMaterialGUI.container.className = 'material-gui-container';
				this.state.selectedMaterialGUI.container.style.display = 'none';
				
				// 将GUI容器添加到页面（放在info display后面）
				if (this.dom.infoDisplay && this.dom.infoDisplay.parentNode) {
					this.dom.infoDisplay.parentNode.insertBefore(
						this.state.selectedMaterialGUI.container,
						this.dom.infoDisplay.nextSibling
					);
				} else {
					// 如果找不到info display，添加到body
					document.body.appendChild(this.state.selectedMaterialGUI.container);
				}
				
				// 确保lil-gui已加载
				if (typeof lil === 'undefined' || !lil.GUI) {
					const script = document.createElement('script');
					script.src = 'https://cdn.jsdelivr.net/npm/lil-gui@0.19.2/dist/lil-gui.umd.js';
					script.onload = () => {
						this.createSelectedMaterialGUI();
					};
					document.head.appendChild(script);
				}
			}

			createSelectedMaterialGUI() {
				if (typeof lil === 'undefined' || !lil.GUI) {
					console.warn('lil-gui not loaded');
					return;
				}
				
				// 如果GUI实例已存在，先销毁
				if (this.state.selectedMaterialGUI.guiInstance) {
					try {
						this.state.selectedMaterialGUI.guiInstance.destroy();
					} catch (e) {
						console.log('Error destroying selected material GUI:', e);
					}
					this.state.selectedMaterialGUI.guiInstance = null;
				}
				
				// 更新标题，包含多重材质信息
				let title = this.state.selectedMaterialGUI.title;
				
				try {
					this.state.selectedMaterialGUI.guiInstance = new lil.GUI({
						container: this.state.selectedMaterialGUI.container,
						autoPlace: false,
						width: 180,
						title: title
					});
					
					// 获取GUI根元素并应用样式
					const guiRoot = this.state.selectedMaterialGUI.container.querySelector('.lil-gui');
					if (guiRoot) {
						guiRoot.style.width = '100%';
						guiRoot.style.maxHeight = '502';
						guiRoot.style.overflowY = 'auto';
						guiRoot.style.padding = '0';
						guiRoot.style.margin = '0';
					}
				} catch (error) {
					console.log('Error creating selected material GUI:', error);
				}
			}

			showSelectedMaterialGUI(object) {
				if (!object) return;
				
				// 处理多重材质的情况
				let material = object.material;
				let isMultiMaterial = false;
				let materialArray = [];
				
				if (Array.isArray(material)) {
					// 如果是材质数组，处理所有材质
					if (material.length === 0) {
						console.warn('Object has empty material array');
						return;
					}
					materialArray = material;
					isMultiMaterial = true;
				} else {
					// 单个材质也放入数组中，统一处理
					materialArray = [material];
				}
				
				// 检查材质是否有效
				for (const mat of materialArray) {
					if (!mat || !mat.type) {
						console.warn('Object has invalid material:', object);
						return;
					}
				}
				
				this.state.selectedMaterialGUI.material = isMultiMaterial ? materialArray[0] : materialArray[0];
				this.state.selectedMaterialGUI.object = object;
				this.state.selectedMaterialGUI.isMultiMaterial = isMultiMaterial;
				this.state.selectedMaterialGUI.materialIndex = 0;
				this.state.selectedMaterialGUI.materialArray = materialArray;
				
				// 创建标题
				let displayTitle = '';
				if (isMultiMaterial) {
					// 多重材质标题 - 修改为: Multi Sub Material (2)
					displayTitle = 'Multi Sub Material (' + materialArray.length + ')';
				} else {
					// 单个材质标题
					let materialType = materialArray[0].type;
					if (typeof materialType === 'string') {
						materialType = materialType.replace('Material', '');
					} else {
						materialType = 'Unknown';
					}
					
					const fullTitle = (materialArray[0].name || 'Unnamed') + ' - ' + materialType;
					const maxTitleLength = 25;
					
					if (fullTitle.length > maxTitleLength) {
						const objectName = materialArray[0].name || 'Material';
						if (objectName.length > 15) {
							const shortObjectName = objectName.substring(0, 12) + '...';
							displayTitle = shortObjectName + ' - ' + materialType;
						} else {
							displayTitle = fullTitle.substring(0, maxTitleLength - 3) + '...';
						}
					} else {
						displayTitle = fullTitle;
					}
				}
				
				this.state.selectedMaterialGUI.title = displayTitle;
				
				// 初始化GUI容器（如果还没有）
				if (!this.state.selectedMaterialGUI.container) {
					this.initSelectedMaterialGUI();
				}
				
				// 创建GUI
				this.createSelectedMaterialGUI();
				
				const gui = this.state.selectedMaterialGUI.guiInstance;
				if (!gui) return;
				
				// 清空现有内容
				gui.children.forEach(child => {
					if (child._controllers) {
						child._controllers.forEach(controller => controller.destroy());
					}
				});
				gui.children.length = 0;
				
				// 如果是多重材质，创建子材质文件夹
				if (isMultiMaterial) {
					for (let i = 0; i < materialArray.length; i++) {
						const subMaterial = materialArray[i];
						
						// 创建子材质文件夹标题
						let subMaterialTitle = '';
						let materialType = subMaterial.type;
						if (typeof materialType === 'string') {
							materialType = materialType.replace('Material', '');
						} else {
							materialType = 'Unknown';
						}
						
						const fullSubTitle = (subMaterial.name || 'Material ' + (i + 1)) + ' - ' + materialType;
						const maxSubTitleLength = 20;
						
						if (fullSubTitle.length > maxSubTitleLength) {
							subMaterialTitle = fullSubTitle.substring(0, maxSubTitleLength - 3) + '...';
						} else {
							subMaterialTitle = fullSubTitle;
						}
						
						// 添加序号 - 保持不变：(1/2), (2/2)等
						subMaterialTitle += ' (' + (i + 1) + '/' + materialArray.length + ')';
						
						// 创建子材质文件夹
						const subMaterialFolder = gui.addFolder(subMaterialTitle);
						
						// 根据材质类型创建对应的GUI
						if (subMaterial.isMeshStandardMaterial) {
							this.createStandardMaterialFolderForSub(subMaterialFolder, subMaterial, i);
						} else if (subMaterial.isMeshBasicMaterial) {
							this.createBasicMaterialFolderForSub(subMaterialFolder, subMaterial, i);
						} else if (subMaterial.isMeshPhongMaterial) {
							this.createPhongMaterialFolderForSub(subMaterialFolder, subMaterial, i);
						} else if (subMaterial.isMeshLambertMaterial) {
							this.createLambertMaterialFolderForSub(subMaterialFolder, subMaterial, i);
						} else if (subMaterial.isMeshToonMaterial) {
							this.createToonMaterialFolderForSub(subMaterialFolder, subMaterial, i);
						} else {
							// 默认显示标准材质GUI
							this.createStandardMaterialFolderForSub(subMaterialFolder, subMaterial, i);
						}
						
						// 默认关闭子材质文件夹
						if (subMaterialFolder && subMaterialFolder.close) {
							subMaterialFolder.close();
						}
					}
				} else {
					// 单个材质，直接创建对应的GUI
					const singleMaterial = materialArray[0];
					
					if (singleMaterial.isMeshStandardMaterial) {
						this.createStandardMaterialFolder(gui, singleMaterial);
					} else if (singleMaterial.isMeshBasicMaterial) {
						this.createBasicMaterialFolder(gui, singleMaterial);
					} else if (singleMaterial.isMeshPhongMaterial) {
						this.createPhongMaterialFolder(gui, singleMaterial);
					} else if (singleMaterial.isMeshLambertMaterial) {
						this.createLambertMaterialFolder(gui, singleMaterial);
					} else if (singleMaterial.isMeshToonMaterial) {
						this.createToonMaterialFolder(gui, singleMaterial);
					} else {
						// 默认显示标准材质GUI
						this.createStandardMaterialFolder(gui, singleMaterial);
					}
				}
				
				// 显示GUI容器
				this.state.selectedMaterialGUI.container.style.display = 'block';
				this.state.selectedMaterialGUI.visible = true;
				
				// 隐藏全局材质GUI
				this.hideMaterialGUI();
			}

			hideSelectedMaterialGUI() {
				if (!this.state.selectedMaterialGUI.container) return;
				
				// 不再清理材质贴图缓存，只隐藏GUI
				this.state.selectedMaterialGUI.container.style.display = 'none';
				this.state.selectedMaterialGUI.visible = false;
				
				// 销毁GUI实例但不清除材质引用
				if (this.state.selectedMaterialGUI.guiInstance) {
					try {
						this.state.selectedMaterialGUI.guiInstance.destroy();
					} catch (e) {
						console.log('Error destroying selected material GUI:', e);
					}
					this.state.selectedMaterialGUI.guiInstance = null;
				}
				
				// 保持材质和对象的引用，不清除它们
				// 只在clearSelection中清除材质引用
			}

			createStandardMaterialFolder(parentFolder, material) {
				// 如果parentFolder是GUI实例，则使用它；否则使用全局的selectedMaterialGUI.guiInstance
				const gui = parentFolder || this.state.selectedMaterialGUI.guiInstance;
				if (!gui) return;
				
				// 清空现有的控制器
				gui.children.forEach(child => {
					if (child._controllers) {
						child._controllers.forEach(controller => controller.destroy());
					}
				});
				gui.children.length = 0;
				
				// 确保材质有纹理缓存
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				// 扫描并缓存材质中的所有现有贴图
				const textureProperties = [
					'map', 'roughnessMap', 'metalnessMap', 'emissiveMap',
					'normalMap', 'bumpMap', 'aoMap', 'displacementMap',
					'alphaMap', 'lightMap', 'envMap'
				];
				
				textureProperties.forEach(prop => {
					if (material[prop] && !material._textureCache[prop]) {
						material._textureCache[prop] = material[prop];
						
						// 确保贴图已加载并可用
						if (material[prop].image) {
							material[prop].needsUpdate = true;
							material.needsUpdate = true;
						}
					}
				});
				
				// 存储folder引用以便更新按钮
				const folderRefs = {};
				
				// 1. Base Color
				const colorFolder = gui.addFolder('Base Color');
				folderRefs.baseColor = colorFolder;
				
				// Base Color
				colorFolder.addColor(material, 'color').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Base Color Map
				this.createTextureControl(colorFolder, material, 'map', {
					label: 'Color Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(colorFolder, 'map', material.map);
					}
				});
				
				// 2. Roughness
				const roughnessFolder = gui.addFolder('Roughness');
				folderRefs.roughness = roughnessFolder;
				
				// Roughness 值
				roughnessFolder.add(material, 'roughness', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Roughness Map
				this.createTextureControl(roughnessFolder, material, 'roughnessMap', {
					label: 'Roughness Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(roughnessFolder, 'roughnessMap', material.roughnessMap);
					}
				});
				
				// 3. Metalness
				const metalnessFolder = gui.addFolder('Metalness');
				folderRefs.metalness = metalnessFolder;
				
				// Metalness 值
				metalnessFolder.add(material, 'metalness', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Metalness Map
				this.createTextureControl(metalnessFolder, material, 'metalnessMap', {
					label: 'Metalness Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(metalnessFolder, 'metalnessMap', material.metalnessMap);
					}
				});
				
				// 4. Emissive
				const emissiveFolder = gui.addFolder('Emissive');
				folderRefs.emissive = emissiveFolder;
				
				// Emissive Color
				emissiveFolder.addColor(material, 'emissive').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Emissive Intensity
				emissiveFolder.add(material, 'emissiveIntensity', 0, 10, 0.1).name('Intensity')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Emissive Map
				this.createTextureControl(emissiveFolder, material, 'emissiveMap', {
					label: 'Emissive Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(emissiveFolder, 'emissiveMap', material.emissiveMap);
					}
				});
				
				// 5. Normal Map
				const normalFolder = gui.addFolder('Normal');
				folderRefs.normal = normalFolder;
				
				// Normal Map
				this.createTextureControl(normalFolder, material, 'normalMap', {
					label: 'Normal Texture',
					hasScale: true,
					scaleProperty: 'normalScale',
					onTextureChange: () => {
						this.updateTextureButtonName(normalFolder, 'normalMap', material.normalMap);
					}
				});
				
				// Normal Scale (如果有贴图或已设置)
				if (material.normalMap || material.normalScale) {
					if (!material.normalScale) {
						material.normalScale = new THREE.Vector2(1, 1);
					}
					normalFolder.add(material.normalScale, 'x', -3, 3, 0.1).name('Scale X')
						.onChange(() => {
							material.needsUpdate = true;
							this.renderInvalidate();
						});
					normalFolder.add(material.normalScale, 'y', -3, 3, 0.1).name('Scale Y')
						.onChange(() => {
							material.needsUpdate = true;
							this.renderInvalidate();
						});
				}
				
				// 6. Bump Map
				const bumpFolder = gui.addFolder('Bump');
				folderRefs.bump = bumpFolder;
				
				// Bump Map
				this.createTextureControl(bumpFolder, material, 'bumpMap', {
					label: 'Bump Texture',
					hasScale: true,
					scaleProperty: 'bumpScale',
					onTextureChange: () => {
						this.updateTextureButtonName(bumpFolder, 'bumpMap', material.bumpMap);
					}
				});
				
				// Bump Scale (如果有贴图或已设置)
				if (material.bumpMap || material.bumpScale !== undefined) {
					if (material.bumpScale === undefined) {
						material.bumpScale = 1;
					}
					bumpFolder.add(material, 'bumpScale', 0, 3, 0.1).name('Scale')
						.onChange(() => {
							material.needsUpdate = true;
							this.renderInvalidate();
						});
				}
				
				// 7. Ambient Occlusion
				const aoFolder = gui.addFolder('Ambient Occlusion');
				folderRefs.ao = aoFolder;
				
				// AO Map
				this.createTextureControl(aoFolder, material, 'aoMap', {
					label: 'AO Texture',
					hasIntensity: true,
					intensityProperty: 'aoMapIntensity',
					onTextureChange: () => {
						this.updateTextureButtonName(aoFolder, 'aoMap', material.aoMap);
					}
				});
				
				// AO Intensity (如果有贴图或已设置)
				if (material.aoMap || material.aoMapIntensity !== undefined) {
					if (material.aoMapIntensity === undefined) {
						material.aoMapIntensity = 1;
					}
					aoFolder.add(material, 'aoMapIntensity', 0, 3, 0.1).name('Intensity')
						.onChange(() => {
							material.needsUpdate = true;
							this.renderInvalidate();
						});
				}
				
				// 8. Displacement
				const displacementFolder = gui.addFolder('Displacement');
				folderRefs.displacement = displacementFolder;
				
				// Displacement Map
				this.createTextureControl(displacementFolder, material, 'displacementMap', {
					label: 'Displacement Texture',
					hasScale: true,
					scaleProperty: 'displacementScale',
					hasBias: true,
					biasProperty: 'displacementBias',
					onTextureChange: () => {
						this.updateTextureButtonName(displacementFolder, 'displacementMap', material.displacementMap);
					}
				});
				
				// Displacement Scale & Bias (如果有贴图或已设置)
				if (material.displacementMap || material.displacementScale !== undefined) {
					if (material.displacementScale === undefined) {
						material.displacementScale = 1;
					}
					if (material.displacementBias === undefined) {
						material.displacementBias = 0;
					}
					
					displacementFolder.add(material, 'displacementScale', 0, 10, 0.1).name('Scale')
						.onChange(() => {
							material.needsUpdate = true;
							this.renderInvalidate();
						});
					displacementFolder.add(material, 'displacementBias', -5, 5, 0.1).name('Bias')
						.onChange(() => {
							material.needsUpdate = true;
							this.renderInvalidate();
						});
				}
				
				// 9. Environment Map
				const envFolder = gui.addFolder('Environment');
				folderRefs.environment = envFolder;
				
				this.createTextureControl(envFolder, material, 'envMap', {
					label: 'Environment Texture',
					isColorMap: true,
					hasIntensity: true,
					intensityProperty: 'envMapIntensity',
					onTextureChange: () => {
						this.updateTextureButtonName(envFolder, 'envMap', material.envMap);
					}
				});
				
				// 10. Light Map
				const lightMapFolder = gui.addFolder('Light');
				folderRefs.light = lightMapFolder;
				
				this.createTextureControl(lightMapFolder, material, 'lightMap', {
					label: 'Light Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(lightMapFolder, 'lightMap', material.lightMap);
					}
				});
				
				// 11. Opacity
				const opacityFolder = gui.addFolder('Opacity');
				folderRefs.opacity = opacityFolder;
				
				// Opacity 值
				opacityFolder.add(material, 'opacity', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.transparent = material.opacity < 1;
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Alpha Map
				this.createTextureControl(opacityFolder, material, 'alphaMap', {
					label: 'Alpha Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(opacityFolder, 'alphaMap', material.alphaMap);
					}
				});
				
				// 12. Other Properties
				const otherFolder = gui.addFolder('Other');
				folderRefs.other = otherFolder;
				
				// Flat Shading
				otherFolder.add(material, 'flatShading').name('Flat Shading')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Vertex Colors
				otherFolder.add(material, 'vertexColors').name('Vertex Colors')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe
				otherFolder.add(material, 'wireframe').name('Wireframe')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe Linewidth
				otherFolder.add(material, 'wireframeLinewidth', 0.1, 5, 0.1).name('Line Width')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// 保存folder引用和材质引用以便后续更新
				if (parentFolder) {
					// 如果是子材质，保存到父文件夹的userData中
					parentFolder.userData = parentFolder.userData || {};
					parentFolder.userData.folderRefs = folderRefs;
					parentFolder.userData.material = material;
				} else {
					// 单个材质，保存到全局
					this.state.selectedMaterialGUI.folderRefs = folderRefs;
					this.state.selectedMaterialGUI.material = material;
				}
				
				// 所有folder默认关闭
				Object.values(folderRefs).forEach(folder => {
					if (folder && folder.close) {
						folder.close();
					}
				});
			}

			createBasicMaterialFolder(parentFolder, material) {
				// 如果parentFolder是GUI实例，则使用它；否则使用全局的selectedMaterialGUI.guiInstance
				const gui = parentFolder || this.state.selectedMaterialGUI.guiInstance;
				if (!gui) return;
				
				// 清空现有的控制器
				gui.children.forEach(child => {
					if (child._controllers) {
						child._controllers.forEach(controller => controller.destroy());
					}
				});
				gui.children.length = 0;
				
				// 确保材质有纹理缓存
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				// 存储folder引用
				const folderRefs = {};
				
				// 1. Base Color
				const colorFolder = gui.addFolder('Base Color');
				folderRefs.baseColor = colorFolder;
				
				colorFolder.addColor(material, 'color').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Base Color Map
				this.createTextureControl(colorFolder, material, 'map', {
					label: 'Color Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(colorFolder, 'basecolor', material.map);
					}
				});
				
				// 2. Environment Map (环境贴图)
				const envFolder = gui.addFolder('Environment');
				folderRefs.environment = envFolder;
				
				this.createTextureControl(envFolder, material, 'envMap', {
					label: 'Environment Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(envFolder, 'env', material.envMap);
					}
				});
				
				// 3. Ambient Occlusion (环境光遮蔽)
				const aoFolder = gui.addFolder('Ambient Occlusion');
				folderRefs.ao = aoFolder;
				
				this.createTextureControl(aoFolder, material, 'aoMap', {
					label: 'AO Texture',
					hasIntensity: true,
					intensityProperty: 'aoMapIntensity',
					onTextureChange: () => {
						this.updateTextureButtonName(aoFolder, 'ao', material.aoMap);
					}
				});
				
				// 4. Opacity (透明度)
				const opacityFolder = gui.addFolder('Opacity');
				folderRefs.opacity = opacityFolder;
				
				opacityFolder.add(material, 'opacity', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.transparent = material.opacity < 1;
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Alpha Map
				this.createTextureControl(opacityFolder, material, 'alphaMap', {
					label: 'Alpha Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(opacityFolder, 'opacity', material.alphaMap);
					}
				});
				
				// 5. Other Properties
				const otherFolder = gui.addFolder('Other');
				folderRefs.other = otherFolder;
				
				// Vertex Colors
				otherFolder.add(material, 'vertexColors').name('Vertex Colors')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe
				otherFolder.add(material, 'wireframe').name('Wireframe')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe Linewidth
				otherFolder.add(material, 'wireframeLinewidth', 0.1, 5, 0.1).name('Line Width')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// 保存folder引用
				this.state.selectedMaterialGUI.folderRefs = folderRefs;
				
				// 默认关闭所有文件夹
				Object.values(folderRefs).forEach(folder => {
					if (folder && folder.close) {
						folder.close();
					}
				});
			}

			createLambertMaterialFolder(parentFolder, material) {
				// 如果parentFolder是GUI实例，则使用它；否则使用全局的selectedMaterialGUI.guiInstance
				const gui = parentFolder || this.state.selectedMaterialGUI.guiInstance;
				if (!gui) return;
				
				// 清空现有的控制器
				gui.children.forEach(child => {
					if (child._controllers) {
						child._controllers.forEach(controller => controller.destroy());
					}
				});
				gui.children.length = 0;
				
				// 确保材质有纹理缓存
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				// 存储folder引用
				const folderRefs = {};
				
				// 1. Base Color
				const colorFolder = gui.addFolder('Base Color');
				folderRefs.baseColor = colorFolder;
				
				colorFolder.addColor(material, 'color').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Base Color Map
				this.createTextureControl(colorFolder, material, 'map', {
					label: 'Color Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(colorFolder, 'baseColor', material.map);
					}
				});
				
				// 2. Emissive (自发光)
				const emissiveFolder = gui.addFolder('Emissive');
				folderRefs.emissive = emissiveFolder;
				
				emissiveFolder.addColor(material, 'emissive').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				emissiveFolder.add(material, 'emissiveIntensity', 0, 10, 0.1).name('Intensity')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Emissive Map
				this.createTextureControl(emissiveFolder, material, 'emissiveMap', {
					label: 'Emissive Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(emissiveFolder, 'emissive', material.emissiveMap);
					}
				});
				
				// 3. Normal Map (法线贴图)
				const normalFolder = gui.addFolder('Normal');
				folderRefs.normal = normalFolder;
				
				this.createTextureControl(normalFolder, material, 'normalMap', {
					label: 'Normal Texture',
					hasScale: true,
					scaleProperty: 'normalScale',
					onTextureChange: () => {
						this.updateTextureButtonName(normalFolder, 'normal', material.normalMap);
					}
				});
				
				// 4. Bump Map (凹凸贴图)
				const bumpFolder = gui.addFolder('Bump');
				folderRefs.bump = bumpFolder;
				
				this.createTextureControl(bumpFolder, material, 'bumpMap', {
					label: 'Bump Texture',
					hasScale: true,
					scaleProperty: 'bumpScale',
					onTextureChange: () => {
						this.updateTextureButtonName(bumpFolder, 'bump', material.bumpMap);
					}
				});
				
				// 5. Displacement Map (位移贴图)
				const displacementFolder = gui.addFolder('Displacement');
				folderRefs.displacement = displacementFolder;
				
				this.createTextureControl(displacementFolder, material, 'displacementMap', {
					label: 'Displacement Texture',
					hasScale: true,
					scaleProperty: 'displacementScale',
					hasBias: true,
					biasProperty: 'displacementBias',
					onTextureChange: () => {
						this.updateTextureButtonName(displacementFolder, 'displacement', material.displacementMap);
					}
				});
				
				// 6. Ambient Occlusion (环境光遮蔽)
				const aoFolder = gui.addFolder('Ambient Occlusion');
				folderRefs.ao = aoFolder;
				
				this.createTextureControl(aoFolder, material, 'aoMap', {
					label: 'AO Texture',
					hasIntensity: true,
					intensityProperty: 'aoMapIntensity',
					onTextureChange: () => {
						this.updateTextureButtonName(aoFolder, 'ao', material.aoMap);
					}
				});
				
				// 7. Environment Map (环境贴图)
				const envFolder = gui.addFolder('Environment');
				folderRefs.environment = envFolder;
				
				this.createTextureControl(envFolder, material, 'envMap', {
					label: 'Environment Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(envFolder, 'environment', material.envMap);
					}
				});
				
				// 8. Light Map (光照贴图)
				const lightMapFolder = gui.addFolder('Light');
				folderRefs.light = lightMapFolder;
				
				this.createTextureControl(lightMapFolder, material, 'lightMap', {
					label: 'Light Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(lightMapFolder, 'light', material.lightMap);
					}
				});
				
				// 9. Opacity (透明度)
				const opacityFolder = gui.addFolder('Opacity');
				folderRefs.opacity = opacityFolder;
				
				opacityFolder.add(material, 'opacity', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.transparent = material.opacity < 1;
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Alpha Map
				this.createTextureControl(opacityFolder, material, 'alphaMap', {
					label: 'Alpha Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(opacityFolder, 'opacity', material.alphaMap);
					}
				});
				
				// 10. Other Properties
				const otherFolder = gui.addFolder('Other');
				folderRefs.other = otherFolder;
				
				// Flat Shading
				otherFolder.add(material, 'flatShading').name('Flat Shading')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Vertex Colors
				otherFolder.add(material, 'vertexColors').name('Vertex Colors')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe
				otherFolder.add(material, 'wireframe').name('Wireframe')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe Linewidth
				otherFolder.add(material, 'wireframeLinewidth', 0.1, 5, 0.1).name('Line Width')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// 保存folder引用
				this.state.selectedMaterialGUI.folderRefs = folderRefs;
				
				// 默认关闭所有文件夹
				Object.values(folderRefs).forEach(folder => {
					if (folder && folder.close) {
						folder.close();
					}
				});
			}

			createPhongMaterialFolder(parentFolder, material) {
				// 如果parentFolder是GUI实例，则使用它；否则使用全局的selectedMaterialGUI.guiInstance
				const gui = parentFolder || this.state.selectedMaterialGUI.guiInstance;
				if (!gui) return;
				
				// 清空现有的控制器
				gui.children.forEach(child => {
					if (child._controllers) {
						child._controllers.forEach(controller => controller.destroy());
					}
				});
				gui.children.length = 0;
				
				// 确保材质有纹理缓存
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				// 存储folder引用
				const folderRefs = {};
				
				// 1. Base Color
				const colorFolder = gui.addFolder('Base Color');
				folderRefs.baseColor = colorFolder;
				
				colorFolder.addColor(material, 'color').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Base Color Map
				this.createTextureControl(colorFolder, material, 'map', {
					label: 'Color Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(colorFolder, 'baseColor', material.map);
					}
				});
				
				// 2. Specular (高光)
				const specularFolder = gui.addFolder('Specular');
				folderRefs.specular = specularFolder;
				
				specularFolder.addColor(material, 'specular').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				specularFolder.add(material, 'shininess', 0, 100, 1).name('Shininess')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Specular Map
				this.createTextureControl(specularFolder, material, 'specularMap', {
					label: 'Specular Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(specularFolder, 'specular', material.specularMap);
					}
				});
				
				// 3. Emissive (自发光)
				const emissiveFolder = gui.addFolder('Emissive');
				folderRefs.emissive = emissiveFolder;
				
				emissiveFolder.addColor(material, 'emissive').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				emissiveFolder.add(material, 'emissiveIntensity', 0, 10, 0.1).name('Intensity')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Emissive Map
				this.createTextureControl(emissiveFolder, material, 'emissiveMap', {
					label: 'Emissive Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(emissiveFolder, 'emissive', material.emissiveMap);
					}
				});
				
				// 4. Normal Map (法线贴图)
				const normalFolder = gui.addFolder('Normal');
				folderRefs.normal = normalFolder;
				
				this.createTextureControl(normalFolder, material, 'normalMap', {
					label: 'Normal Texture',
					hasScale: true,
					scaleProperty: 'normalScale',
					onTextureChange: () => {
						this.updateTextureButtonName(normalFolder, 'normal', material.normalMap);
					}
				});
				
				// 5. Bump Map (凹凸贴图)
				const bumpFolder = gui.addFolder('Bump');
				folderRefs.bump = bumpFolder;
				
				this.createTextureControl(bumpFolder, material, 'bumpMap', {
					label: 'Bump Texture',
					hasScale: true,
					scaleProperty: 'bumpScale',
					onTextureChange: () => {
						this.updateTextureButtonName(bumpFolder, 'bump', material.bumpMap);
					}
				});
				
				// 6. Displacement Map (位移贴图)
				const displacementFolder = gui.addFolder('Displacement');
				folderRefs.displacement = displacementFolder;
				
				this.createTextureControl(displacementFolder, material, 'displacementMap', {
					label: 'Displacement Texture',
					hasScale: true,
					scaleProperty: 'displacementScale',
					hasBias: true,
					biasProperty: 'displacementBias',
					onTextureChange: () => {
						this.updateTextureButtonName(displacementFolder, 'displacement', material.displacementMap);
					}
				});
				
				// 7. Ambient Occlusion (环境光遮蔽)
				const aoFolder = gui.addFolder('Ambient Occlusion');
				folderRefs.ao = aoFolder;
				
				this.createTextureControl(aoFolder, material, 'aoMap', {
					label: 'AO Texture',
					hasIntensity: true,
					intensityProperty: 'aoMapIntensity',
					onTextureChange: () => {
						this.updateTextureButtonName(aoFolder, 'ao', material.aoMap);
					}
				});
				
				// 8. Environment Map (环境贴图)
				const envFolder = gui.addFolder('Environment');
				folderRefs.environment = envFolder;
				
				this.createTextureControl(envFolder, material, 'envMap', {
					label: 'Environment Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(envFolder, 'environment', material.envMap);
					}
				});
				
				// 9. Light Map (光照贴图)
				const lightMapFolder = gui.addFolder('Light');
				folderRefs.light = lightMapFolder;
				
				this.createTextureControl(lightMapFolder, material, 'lightMap', {
					label: 'Light Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(lightMapFolder, 'light', material.lightMap);
					}
				});
				
				// 10. Opacity (透明度)
				const opacityFolder = gui.addFolder('Opacity');
				folderRefs.opacity = opacityFolder;
				
				opacityFolder.add(material, 'opacity', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.transparent = material.opacity < 1;
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Alpha Map
				this.createTextureControl(opacityFolder, material, 'alphaMap', {
					label: 'Alpha Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(opacityFolder, 'opacity', material.alphaMap);
					}
				});
				
				// 11. Other Properties
				const otherFolder = gui.addFolder('Other');
				folderRefs.other = otherFolder;
				
				// Flat Shading
				otherFolder.add(material, 'flatShading').name('Flat Shading')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Vertex Colors
				otherFolder.add(material, 'vertexColors').name('Vertex Colors')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe
				otherFolder.add(material, 'wireframe').name('Wireframe')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe Linewidth
				otherFolder.add(material, 'wireframeLinewidth', 0.1, 5, 0.1).name('Line Width')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// 保存folder引用
				this.state.selectedMaterialGUI.folderRefs = folderRefs;
				
				// 默认关闭所有文件夹
				Object.values(folderRefs).forEach(folder => {
					if (folder && folder.close) {
						folder.close();
					}
				});
			}

			createToonMaterialFolder(parentFolder, material) {
				// 如果parentFolder是GUI实例，则使用它；否则使用全局的selectedMaterialGUI.guiInstance
				const gui = parentFolder || this.state.selectedMaterialGUI.guiInstance;
				if (!gui) return;
				
				// 清空现有的控制器
				gui.children.forEach(child => {
					if (child._controllers) {
						child._controllers.forEach(controller => controller.destroy());
					}
				});
				gui.children.length = 0;
				
				// 确保材质有纹理缓存
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				// 存储folder引用
				const folderRefs = {};
				
				// 1. Base Color
				const colorFolder = gui.addFolder('Base Color');
				folderRefs.baseColor = colorFolder;
				
				colorFolder.addColor(material, 'color').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Base Color Map
				this.createTextureControl(colorFolder, material, 'map', {
					label: 'Color Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(colorFolder, 'baseColor', material.map);
					}
				});
				
				// 2. Gradient Map (渐变贴图) - Toon材质特有
				const gradientFolder = gui.addFolder('Gradient');
				folderRefs.gradient = gradientFolder;
				
				this.createTextureControl(gradientFolder, material, 'gradientMap', {
					label: 'Gradient Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(gradientFolder, 'gradient', material.gradientMap);
					}
				});
				
				// 3. Emissive (自发光)
				const emissiveFolder = gui.addFolder('Emissive');
				folderRefs.emissive = emissiveFolder;
				
				emissiveFolder.addColor(material, 'emissive').name('Color')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				emissiveFolder.add(material, 'emissiveIntensity', 0, 10, 0.1).name('Intensity')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Emissive Map
				this.createTextureControl(emissiveFolder, material, 'emissiveMap', {
					label: 'Emissive Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(emissiveFolder, 'emissive', material.emissiveMap);
					}
				});
				
				// 4. Normal Map (法线贴图)
				const normalFolder = gui.addFolder('Normal');
				folderRefs.normal = normalFolder;
				
				this.createTextureControl(normalFolder, material, 'normalMap', {
					label: 'Normal Texture',
					hasScale: true,
					scaleProperty: 'normalScale',
					onTextureChange: () => {
						this.updateTextureButtonName(normalFolder, 'normal', material.normalMap);
					}
				});
				
				// 5. Bump Map (凹凸贴图)
				const bumpFolder = gui.addFolder('Bump');
				folderRefs.bump = bumpFolder;
				
				this.createTextureControl(bumpFolder, material, 'bumpMap', {
					label: 'Bump Texture',
					hasScale: true,
					scaleProperty: 'bumpScale',
					onTextureChange: () => {
						this.updateTextureButtonName(bumpFolder, 'bump', material.bumpMap);
					}
				});
				
				// 6. Displacement Map (位移贴图)
				const displacementFolder = gui.addFolder('Displacement');
				folderRefs.displacement = displacementFolder;
				
				this.createTextureControl(displacementFolder, material, 'displacementMap', {
					label: 'Displacement Texture',
					hasScale: true,
					scaleProperty: 'displacementScale',
					hasBias: true,
					biasProperty: 'displacementBias',
					onTextureChange: () => {
						this.updateTextureButtonName(displacementFolder, 'displacement', material.displacementMap);
					}
				});
				
				// 7. Ambient Occlusion (环境光遮蔽)
				const aoFolder = gui.addFolder('Ambient Occlusion');
				folderRefs.ao = aoFolder;
				
				this.createTextureControl(aoFolder, material, 'aoMap', {
					label: 'AO Texture',
					hasIntensity: true,
					intensityProperty: 'aoMapIntensity',
					onTextureChange: () => {
						this.updateTextureButtonName(aoFolder, 'ao', material.aoMap);
					}
				});
				
				// 8. Environment Map (环境贴图)
				const envFolder = gui.addFolder('Environment');
				folderRefs.environment = envFolder;
				
				this.createTextureControl(envFolder, material, 'envMap', {
					label: 'Environment Texture',
					isColorMap: true,
					onTextureChange: () => {
						this.updateTextureButtonName(envFolder, 'environment', material.envMap);
					}
				});
				
				// 9. Light Map (光照贴图)
				const lightMapFolder = gui.addFolder('Light');
				folderRefs.light = lightMapFolder;
				
				this.createTextureControl(lightMapFolder, material, 'lightMap', {
					label: 'Light Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(lightMapFolder, 'light', material.lightMap);
					}
				});
				
				// 10. Opacity (透明度)
				const opacityFolder = gui.addFolder('Opacity');
				folderRefs.opacity = opacityFolder;
				
				opacityFolder.add(material, 'opacity', 0, 1, 0.01).name('Value')
					.onChange(() => {
						material.transparent = material.opacity < 1;
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Alpha Map
				this.createTextureControl(opacityFolder, material, 'alphaMap', {
					label: 'Alpha Texture',
					onTextureChange: () => {
						this.updateTextureButtonName(opacityFolder, 'opacity', material.alphaMap);
					}
				});
				
				// 11. Other Properties
				const otherFolder = gui.addFolder('Other');
				folderRefs.other = otherFolder;
				
				// Vertex Colors
				otherFolder.add(material, 'vertexColors').name('Vertex Colors')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe
				otherFolder.add(material, 'wireframe').name('Wireframe')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// Wireframe Linewidth
				otherFolder.add(material, 'wireframeLinewidth', 0.1, 5, 0.1).name('Line Width')
					.onChange(() => {
						material.needsUpdate = true;
						this.renderInvalidate();
					});
				
				// 保存folder引用
				this.state.selectedMaterialGUI.folderRefs = folderRefs;
				
				// 默认关闭所有文件夹
				Object.values(folderRefs).forEach(folder => {
					if (folder && folder.close) {
						folder.close();
					}
				});
			}

			createStandardMaterialFolderForSub(parentFolder, material, index) {
				this.createStandardMaterialFolder(parentFolder, material);
			}

			createBasicMaterialFolderForSub(parentFolder, material, index) {
				this.createBasicMaterialFolder(parentFolder, material);
			}

			createPhongMaterialFolderForSub(parentFolder, material, index) {
				this.createPhongMaterialFolder(parentFolder, material);
			}

			createLambertMaterialFolderForSub(parentFolder, material, index) {
				this.createLambertMaterialFolder(parentFolder, material);
			}

			createToonMaterialFolderForSub(parentFolder, material, index) {
				this.createToonMaterialFolder(parentFolder, material);
			}

			createTextureControl(folder, material, propertyName, config = {}) {
				const {
					label = propertyName,
					isColorMap = false,
					hasScale = false,
					scaleProperty = null,
					hasIntensity = false,
					intensityProperty = null,
					hasBias = false,
					biasProperty = null,
					onTextureChange = null
				} = config;
				
				// 确保材质有纹理缓存
				if (!material._textureCache) {
					material._textureCache = {};
				}
				
				// 检查是否有贴图（当前应用或缓存中）
				const currentTexture = material[propertyName] || material._textureCache[propertyName];
				const hasTexture = !!currentTexture;
				
				// 创建贴图操作对象
				const textureActions = {
					action: () => {
						if (material[propertyName] || material._textureCache[propertyName]) {
							// 有贴图：执行移除操作
							this.textureManager.removeTexture(material, propertyName);
							
							// **立即更新GUI控件**
							this.updateTextureUIAfterAction(folder, propertyName, material, false);
							
							if (onTextureChange) {
								onTextureChange();
							}
							
							// **立即强制渲染**
							this.renderInvalidate();
						} else {
							// 无贴图：执行加载操作
							this.textureManager.loadTexture(material, propertyName, isColorMap).then((texture) => {
								if (texture) {
									// **立即更新GUI控件**
									this.updateTextureUIAfterAction(folder, propertyName, material, true, texture);
									
									if (onTextureChange) {
										onTextureChange();
									}
									
									// **立即强制渲染**
									this.renderInvalidate();
								}
							}).catch((error) => {
								console.log('Texture loading cancelled:', error);
							});
						}
					}
				};
				
				// 创建按钮
				let initialButtonName;
				if (currentTexture) {
					const textureName = this.getTextureDisplayName(currentTexture);
					initialButtonName = 'Remove ' + textureName;
				} else {
					initialButtonName = 'Load Texture';
				}
				
				const buttonController = folder.add(textureActions, 'action').name(initialButtonName);
				
				// 创建贴图开关
				const state = {
					useTexture: !!material[propertyName]
				};
				
				const toggleController = folder.add(state, 'useTexture').name('Texture Enabled')
					.onChange((value) => {
						if (value && !material._textureCache[propertyName]) {
							// 没有贴图文件，但试图启用，应该先加载贴图
							console.log('No texture file to enable. Please load a texture first.');
							toggleController.setValue(false);
							return;
						}
						
						this.textureManager.toggleTexture(material, propertyName, value);
						this.renderInvalidate();
						
						if (onTextureChange) {
							onTextureChange();
						}
					});
				
				// 保存引用
				folder._textureButtons = folder._textureButtons || {};
				folder._textureButtons[propertyName] = {
					controller: buttonController,
					toggleController: toggleController,
					actions: textureActions,
					config: config,
					material: material
				};
				
				return {
					button: buttonController,
					toggle: toggleController
				};
			}

			updateTextureUIAfterAction(folder, propertyName, material, hasTexture, texture = null) {
				if (!folder || !folder._textureButtons || !folder._textureButtons[propertyName]) return;
				
				const buttonInfo = folder._textureButtons[propertyName];
				
				// 更新材质状态（确保缓存同步）
				const currentTexture = texture || material[propertyName] || material._textureCache[propertyName];
				const hasTextureFile = !!currentTexture;
				const isTextureApplied = !!material[propertyName];
				
				// 更新按钮文字
				if (buttonInfo.controller) {
					if (hasTextureFile) {
						const textureName = this.getTextureDisplayName(currentTexture);
						buttonInfo.controller.name('Remove ' + textureName);
						
						// 更新按钮动作
						buttonInfo.actions.action = () => {
							this.textureManager.removeTexture(material, propertyName);
							this.updateTextureUIAfterAction(folder, propertyName, material, false);
							this.renderInvalidate();
						};
					} else {
						buttonInfo.controller.name('Load Texture');
						
						// 更新按钮动作
						buttonInfo.actions.action = () => {
							this.textureManager.loadTexture(material, propertyName, buttonInfo.config.isColorMap).then((newTexture) => {
								if (newTexture) {
									this.updateTextureUIAfterAction(folder, propertyName, material, true, newTexture);
									this.renderInvalidate();
								}
							}).catch((error) => {
								console.log('Texture loading cancelled:', error);
							});
						};
					}
					
					// 更新控制器显示
					if (buttonInfo.controller.updateDisplay) {
						buttonInfo.controller.updateDisplay();
					}
				}
				
				// 更新toggle状态
				if (buttonInfo.toggleController) {
					// 先保存当前值，防止触发onChange事件
					const currentValue = buttonInfo.toggleController.getValue();
					const newValue = isTextureApplied;
					
					if (currentValue !== newValue) {
						buttonInfo.toggleController.setValue(newValue);
						
						// 确保toggle的onChange事件被触发
						if (buttonInfo.toggleController._onChange) {
							buttonInfo.toggleController._onChange(newValue);
						}
					}
				}
			}

			updateTextureButtonName(folder, propertyName, texture) {
				if (!folder || !folder._textureButtons || !folder._textureButtons[propertyName]) return;
				
				const buttonInfo = folder._textureButtons[propertyName];
				if (buttonInfo && buttonInfo.controller) {
					// 检查是否有贴图文件（不只是是否应用）
					const hasTextureFile = !!buttonInfo.material._textureCache[propertyName];
					
					if (hasTextureFile) {
						// 有贴图文件：显示Remove按钮
						const textureInCache = buttonInfo.material._textureCache[propertyName];
						const textureName = this.getTextureDisplayName(textureInCache);
						buttonInfo.controller.name('Remove ' + textureName);
						
						// 更新按钮动作为移除贴图
						buttonInfo.actions.action = () => {
							this.textureManager.removeTexture(buttonInfo.material, propertyName);
							
							// 更新按钮文字为Load Texture
							buttonInfo.controller.name('Load Texture');
							buttonInfo.controller.updateDisplay();
							
							// 更新toggle状态为false（因为贴图文件已移除）
							if (buttonInfo.toggleController) {
								buttonInfo.toggleController.setValue(false);
							}
							
							this.renderInvalidate();
						};
					} else {
						// 无贴图文件：显示Load按钮
						buttonInfo.controller.name('Load Texture');
						
						// 更新按钮动作为加载贴图
						buttonInfo.actions.action = () => {
							this.textureManager.loadTexture(buttonInfo.material, propertyName, buttonInfo.config.isColorMap).then((newTexture) => {
								if (newTexture) {
									// 更新按钮文字
									const textureName = this.getTextureDisplayName(newTexture);
									buttonInfo.controller.name('Remove ' + textureName);
									buttonInfo.controller.updateDisplay();
									
									// 更新toggle状态为true（加载后自动启用）
									if (buttonInfo.toggleController) {
										buttonInfo.toggleController.setValue(true);
									}
									
									this.renderInvalidate();
								}
							}).catch((error) => {
								console.log('Texture loading cancelled:', error);
							});
						};
					}
					
					// 更新控制器显示
					if (buttonInfo.controller.updateDisplay) {
						buttonInfo.controller.updateDisplay();
					}
				}
			}

			getTextureDisplayName(texture) {
				if (!texture || !texture.isTexture) return 'Texture';
				
				let textureName = 'Texture';
				
				// 1. 优先从userData获取文件名
				if (texture.userData && texture.userData.filename) {
					textureName = texture.userData.filename;
				}
				// 2. 从原始文件名获取
				else if (texture.image && texture.image.currentSrc) {
					const src = texture.image.currentSrc;
					const filename = src.split('/').pop().split('?')[0];
					if (filename && filename.length > 0) {
						textureName = filename;
					}
				}
				// 3. 从image.src获取
				else if (texture.image && texture.image.src) {
					const src = texture.image.src;
					if (!src.startsWith('data:')) {
						const filename = src.split('/').pop().split('?')[0];
						if (filename && filename.length > 0) {
							textureName = filename;
						}
					}
				}
				// 4. 从texture.name获取
				else if (texture.name) {
					textureName = texture.name;
				}
				// 5. 使用UUID（作为最后备选）
				else if (texture.uuid) {
					textureName = 'Texture-' + texture.uuid.substring(0, 8);
				}
				
				// 限制名称长度
				if (textureName.length > 20) {
					textureName = textureName.substring(0, 17) + '...';
				}
				
				return textureName;
			}

			addTextureParameterControllers(folder, material, propertyName, config) {
				const { hasScale, scaleProperty, hasIntensity, intensityProperty, hasBias, biasProperty } = config;
				
				// 清理已存在的参数控制器
				if (folder._paramControllers) {
					folder._paramControllers.forEach(controller => {
						if (controller && controller.destroy) {
							controller.destroy();
						}
					});
				}
				folder._paramControllers = [];
				
				// 添加缩放控制器
				if (hasScale && scaleProperty) {
					if (material[scaleProperty] !== undefined) {
						if (typeof material[scaleProperty] === 'object' && material[scaleProperty].x !== undefined) {
							// 向量缩放
							const xController = folder.add(material[scaleProperty], 'x', -3, 3, 0.1)
								.name('Scale X')
								.onChange(() => {
									material.needsUpdate = true;
									this.renderInvalidate();
								});
							folder._paramControllers.push(xController);
							
							const yController = folder.add(material[scaleProperty], 'y', -3, 3, 0.1)
								.name('Scale Y')
								.onChange(() => {
									material.needsUpdate = true;
									this.renderInvalidate();
								});
							folder._paramControllers.push(yController);
						} else {
							// 标量缩放
							const scaleController = folder.add(material, scaleProperty, 0, 3, 0.1)
								.name('Scale')
								.onChange(() => {
									material.needsUpdate = true;
									this.renderInvalidate();
								});
							folder._paramControllers.push(scaleController);
						}
					}
				}
				
				// 添加强度控制器
				if (hasIntensity && intensityProperty) {
					if (material[intensityProperty] !== undefined) {
						const intensityController = folder.add(material, intensityProperty, 0, 3, 0.1)
							.name('Intensity')
							.onChange(() => {
								material.needsUpdate = true;
								this.renderInvalidate();
							});
						folder._paramControllers.push(intensityController);
					}
				}
				
				// 添加偏移控制器
				if (hasBias && biasProperty) {
					if (material[biasProperty] !== undefined) {
						const biasController = folder.add(material, biasProperty, -5, 5, 0.1)
							.name('Bias')
							.onChange(() => {
								material.needsUpdate = true;
								this.renderInvalidate();
							});
						folder._paramControllers.push(biasController);
					}
				}
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
					} catch (e) {}
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
					
				} catch (error) {}
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

			createDirLightFolder(open = false) {
				if (!this.state.lightGUI.guiInstance) return;
				
				if (this.state.lightGUI.dirLightFolder) {
					try {
						this.state.lightGUI.dirLightFolder.destroy();
					} catch (e) {}
					this.state.lightGUI.dirLightFolder = null;
				}
				
				const dirLightFolder = this.state.lightGUI.guiInstance.addFolder('Default Directional Light');
				
				this.state.lightGUI.dirLightFolder = dirLightFolder;
				
				const colorController = dirLightFolder.addColor(this.state.lights, 'dirColor')
					.onChange((value) => {
						this.state.lights.dirColor = value;
						this.updateDirLightColor();
					}).name('Color');
				
				const intensityController = dirLightFolder.add(this.state.lights, 'dirIntensity', 0, 10, 0.01)
					.onChange((value) => {
						this.state.lights.dirIntensity = value;
						this.updateDirLightIntensity();
					}).name('Intensity');
				
				dirLightFolder.add({
					reset: () => this.resetDirLightParameters('main')
				}, 'reset').name('Reset');
				
				const poseControllers = {};
				
				poseControllers.azimuth = dirLightFolder.add(this.state.lights.dirSpherical, 'azimuth', 0, 360, 0.01)
					.onChange((value) => {
						this.state.lights.dirSpherical.azimuth = value;
						this.updateDirLightFromSpherical();
					}).name('Azimuth');
				
				poseControllers.elevation = dirLightFolder.add(this.state.lights.dirSpherical, 'elevation', -90, 90, 0.01)
					.onChange((value) => {
						this.state.lights.dirSpherical.elevation = value;
						this.updateDirLightFromSpherical();
					}).name('Elevation');
				
				poseControllers.radius = dirLightFolder.add(this.state.lights.dirSpherical, 'radius', 1, 1000, 0.01)
					.onChange((value) => {
						this.state.lights.dirSpherical.radius = value;
						this.updateDirLightFromSpherical();
					}).name('Distance');
				
				dirLightFolder.add({
					reset: () => this.resetDirLightParameters('pose')
				}, 'reset').name('Reset Pose');
				
				const shadowControllers = {};
				/* 
				shadowControllers.type = dirLightFolder.add(this.state.lights, 'shadowType', {
					'Basic': 'basic',
					'PCF': 'pcf',
					'PCF Soft': 'pcfsoft',
					'VSM': 'vsm'
				}).onChange((value) => {
					this.state.lights.shadowSettings.shadowType = value;
					this.updateShadowType();
				}).name('Shadow Type');
				
				shadowControllers.size = dirLightFolder.add(this.state.lights.shadowSettings, 'mapSize', [512, 1024, 2048, 4096])
					.onChange((value) => {
						this.state.lights.shadowSettings.mapSize = value;
						this.updateShadowSettings();
					}).name('Shadow Map Size');
				
				shadowControllers.blur = dirLightFolder.add(this.state.lights.shadowSettings, 'radius', 0, 10, 1)
					.onChange((value) => {
						this.state.lights.shadowSettings.radius = value;
						this.updateShadowSettings();
					}).name('Shadow Blur Radius');
				
				shadowControllers.samples = dirLightFolder.add(this.state.lights.shadowSettings, 'samples', 1, 32, 1)
					.onChange((value) => {
						this.state.lights.shadowSettings.samples = value;
						this.updateShadowSettings();
					}).name('Shadow Blur Samples');
				*/
				shadowControllers.bias = dirLightFolder.add(this.state.lights.shadowSettings, 'bias', -0.01, 0.01, 0.0001)
					.onChange((value) => {
						this.state.lights.shadowSettings.bias = value;
						this.updateShadowSettings();
						}).name('Shadow Bias');
				
				shadowControllers.normalBias = dirLightFolder.add(this.state.lights.shadowSettings, 'normalBias', 0, 0.1, 0.001)
					.onChange((value) => {
						this.state.lights.shadowSettings.normalBias = value;
						this.updateShadowSettings();
					}).name('Shadow Normal Bias');
				
				shadowControllers.near = dirLightFolder.add(this.state.lights.shadowSettings.camera, 'near', 0.01, 100, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.near = value;
						this.updateShadowSettings();
					}).name('Shadow Near');
				
				shadowControllers.far = dirLightFolder.add(this.state.lights.shadowSettings.camera, 'far', 10, 2000, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.far = value;
						this.updateShadowSettings();
					}).name('Shadow Far');
				
				shadowControllers.left = dirLightFolder.add(this.state.lights.shadowSettings.camera, 'left', -1000, 0, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.left = value;
						this.updateShadowSettings();
					}).name('Shadow Left');
				
				shadowControllers.right = dirLightFolder.add(this.state.lights.shadowSettings.camera, 'right', 0, 1000, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.right = value;
						this.updateShadowSettings();
					}).name('Shadow Right');
				
				shadowControllers.top = dirLightFolder.add(this.state.lights.shadowSettings.camera, 'top', 0, 1000, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.top = value;
						this.updateShadowSettings();
					}).name('Shadow Top');
				
				shadowControllers.bottom = dirLightFolder.add(this.state.lights.shadowSettings.camera, 'bottom', -1000, 0, 0.01)
					.onChange((value) => {
						this.state.lights.shadowSettings.camera.bottom = value;
						this.updateShadowSettings();
					}).name('Shadow Bottom');
				
				dirLightFolder.add({
					reset: () => this.resetDirLightParameters('shadow')
				}, 'reset').name('Reset Shadow Map');
				
				this.state.lightGUI.dirLightControllers = {
					color: colorController,
					intensity: intensityController,
					pose: poseControllers,
					shadow: shadowControllers
				};
				
				if (open) {
					dirLightFolder.open();
				} else {
					dirLightFolder.close();
				}
			}

			createAmbLightFolder(open = false) {
				if (!this.state.lightGUI.guiInstance) return;
				
				if (this.state.lightGUI.ambLightFolder) {
					try {
						this.state.lightGUI.ambLightFolder.destroy();
					} catch (e) {}
					this.state.lightGUI.ambLightFolder = null;
				}
				
				const ambLightFolder = this.state.lightGUI.guiInstance.addFolder('Default Ambient Light');
				
				this.state.lightGUI.ambLightFolder = ambLightFolder;
				
				const colorController = ambLightFolder.addColor(this.state.lights, 'ambColor')
					.onChange((value) => {
						this.state.lights.ambColor = value;
						this.updateAmbLightColor();
					}).name('Color');
				
				const intensityController = ambLightFolder.add(this.state.lights, 'ambIntensity', 0, 10, 0.01)
					.onChange((value) => {
						this.state.lights.ambIntensity = value;
						this.updateAmbLightIntensity();
					}).name('Intensity');
				
				ambLightFolder.add({
					reset: () => this.resetAmbLightParameters()
				}, 'reset').name('Reset');
				
				this.state.lightGUI.ambLightControllers = {
					color: colorController,
					intensity: intensityController
				};
				
				if (open) {
					ambLightFolder.open();
				} else {
					ambLightFolder.close();
				}
			}

			// 模型导入
			handleImportFile(event) {
				const file = event.target.files[0];
				if (file) {
					const fileName = file.name;
					const format = this.detectFormat(fileName);
					const reader = new FileReader();
					
					reader.onload = (e) => this.load3DDataFromBuffer(e.target.result, fileName, format);
					
					if (['zip', 'bin', 'fbx', 'glb', 'ply'].includes(format)) {
						reader.readAsArrayBuffer(file);
					} else {
						reader.readAsText(file);
					}
				}
				event.target.value = '';
			}

			async handleImportMessage(event) {
				if (event.data.type === 'loadData') {
					const filename = event.data.filename;
					const format = this.detectFormat(filename);
					await this.load3DDataFromComfyUI(filename, format);
				}
			}

			detectFormat(filename) { 
				const ext = filename.split('.').pop().toLowerCase(); 
				const map = { 
					'glb': 'glb', 
					'gltf': 'glb', 
					'fbx': 'fbx', 
					'obj': 'obj', 
					'ply': 'ply', 
					'bin': 'bin',
					'zip': 'zip'
				}; 
				return map[ext] || 'glb'; 
			}

			async load3DDataFromBuffer(buffer, filename, format) {
				this.loadingProgress.start('Processing ' + format.toUpperCase() + ' from buffer...', 50);
				await this.processModelLoading(filename, format, async () => {
					await this.loadAndParseFromBuffer(buffer, format);
				});
			}

			async loadAndParseFromBuffer(buffer, format) {
				try {
					this.loadingProgress.update('Parsing ' + format.toUpperCase() + ' data...', 70);
					
					switch(format) {
						case 'bin':
							await this.loadSMPLBinFromBuffer(buffer);
							break;
						case 'glb':
							await this.loadGLBFromBuffer(buffer);
							break;
						case 'fbx':
							await this.loadFBXFromBuffer(buffer);
							break;
						case 'obj':
							await this.loadOBJFromBuffer(buffer);
							break;
						case 'ply':
							await this.loadPLYFromBuffer(buffer);
							break;
						case 'zip':
							await this.loadZipDataFromBuffer(buffer);
							break;
						default:
							throw new Error("Unsupported format: " + format);
					}
					
					this.loadingProgress.update(format.toUpperCase() + ' processing complete', 98);
					
				} catch (error) {
					this.loadingProgress.error('Failed to parse ' + format + ': ' + error.message);
					throw error;
				}
			}

			async load3DDataFromComfyUI(filename, format) {
				if (!filename) throw new Error("No filename provided");
				this.loadingProgress.start('Processing ' + format.toUpperCase() + ' from ComfyUI...', 50);
				await this.processModelLoading(filename, format, async () => {
					await this.loadAndParseFromComfyUI(filename, format);
				});
			}

			async loadAndParseFromComfyUI(filename, format) {
				const formatConfig = {
					'bin': {
						responseType: 'arraybuffer',
						label: 'SMPL',
						progressMessage: (percent, loaded, total) => 'Downloading SMPL: ' + percent + '%'
					},
					'glb': {
						responseType: 'arraybuffer',
						label: 'GLB',
						progressMessage: (percent, loaded, total) => 'Downloading GLB: ' + percent + '%'
					},
					'fbx': {
						responseType: 'arraybuffer',
						label: 'FBX',
						progressMessage: (percent, loaded, total) => 'Downloading FBX: ' + percent + '%'
					},
					'obj': {
						responseType: 'text',
						label: 'OBJ',
						progressMessage: (percent, loaded, total) => 'Downloading OBJ: ' + percent + '%'
					},
					'ply': {
						responseType: 'arraybuffer',
						label: 'PLY',
						progressMessage: (percent, loaded, total) => 'Downloading PLY: ' + percent + '%'
					},
					'zip': {
						responseType: 'arraybuffer',
						label: 'ZIP',
						progressMessage: (percent, loaded, total) => 'Downloading ZIP: ' + percent + '%'
					}
				};
				
				const config = formatConfig[format];
				if (!config) {
					throw new Error('Unsupported format: ' + format);
				}
				
				try {
					// 1: 下载文件
					const result = await this.downloadFileWithProgress(filename, {
						responseType: config.responseType,
						startProgress: 30,
						endProgress: 80,
						label: config.label,
						onProgress: config.progressMessage
					});
					
					// 2: 解析文件
					this.loadingProgress.update('Parsing ' + config.label + ' data...', 85);
					
					switch(format) {
						case 'bin':
							await this.loadSMPLBinFromBuffer(result.data);
							break;
						case 'glb':
							await this.loadGLBFromBuffer(result.data);
							break;
						case 'fbx':
							await this.loadFBXFromBuffer(result.data);
							break;
						case 'obj':
							await this.loadOBJFromBuffer(result.data);
							break;
						case 'ply':
							await this.loadPLYFromBuffer(result.data);
							break;
						case 'zip':
							await this.loadZipDataFromBuffer(result.data);
							break;
					}
					
					this.loadingProgress.update(config.label + ' processing complete', 98);
					
				} catch (error) {
					this.loadingProgress.error('Failed to load ' + config.label + ': ' + error.message);
					throw error;
				}
			}

			async downloadFileWithProgress(filename, options = {}) {
				const {
					responseType = 'arraybuffer',
					startProgress = 30,
					endProgress = 80,
					label = 'Downloading',
					onProgress = null
				} = options;
				
				return new Promise((resolve, reject) => {
					this.loadingProgress.update(label + '...', startProgress);
					
					const xhr = new XMLHttpRequest();
					xhr.open('GET', '/adv3dviewer_jk?filename=' + encodeURIComponent(filename), true);
					xhr.responseType = responseType;
					
					let lastPercent = 0;
					xhr.onprogress = (event) => {
						if (event.lengthComputable) {
							const percentComplete = startProgress + (event.loaded / event.total) * (endProgress - startProgress);
							if (percentComplete - lastPercent >= 1) {
								lastPercent = percentComplete;
								const downloadPercent = Math.round(((percentComplete - startProgress) / (endProgress - startProgress)) * 100);
								const message = onProgress ? onProgress(downloadPercent, event.loaded, event.total) 
														   : label + ': ' + downloadPercent + '%';
								this.loadingProgress.update(message, percentComplete);
							}
						} else {
							const loadedMB = event.loaded / (1024 * 1024);
							const percentComplete = startProgress + Math.min(endProgress - startProgress, loadedMB * 10);
							const message = onProgress ? onProgress(null, event.loaded, null) 
													   : label + ': ' + loadedMB.toFixed(1) + 'MB';
							this.loadingProgress.update(message, percentComplete);
						}
					};
					
					xhr.onload = () => {
						if (xhr.status === 200) {
							resolve({
								data: xhr.response,
								status: xhr.status,
								size: xhr.response.byteLength || xhr.response.length
							});
						} else {
							reject(new Error('Failed to download file: ' + xhr.statusText));
						}
					};
					
					xhr.onerror = () => {
						reject(new Error('Network error while downloading file'));
					};
					
					xhr.send();
				});
			}

			async processModelLoading(filename, format, loadOperation) {
				if (this.state.loading) return;
				this.state.loading = true; 
				
				this.disableControls();
				await new Promise(resolve => setTimeout(resolve, 50));
				
				this.loadingProgress.start('Loading ' + filename + '...', 0);
				
				if (this.state.playback.isPlaying) this.pause();
				this.state.playback.totalFrames = 0;
				
				try {
					this.state.currentFormat = format;
					this.state.currentFileData = { filename, format };
					
					this.loadingProgress.update("Cleaning up previous model...", 10);
					await this.cleanupPreviousModel();
					
					this.loadingProgress.update("Starting model loading...", 20);
					await loadOperation();
					
					this.loadingProgress.update("Finalizing model...", 95);
					this.postModelLoading();
					
					this.loadingProgress.stop("Model loaded successfully");
					
				} catch (e) { 
					this.loadingProgress.error('Error: ' + e.message);
					throw e;
				} finally { 
					this.state.loading = false; 
					
					setTimeout(() => {
						if (!this.state.loading && !this._messageTimer) {
							this.dom.loading.style.display = 'none';
						}
					}, 500);
					
					this.enableControls();
				}
			}

			postModelLoading() {
				this.applyMaterialMode();
				this.updateVisuals(this.state.playback.currentFrame);
				this.updateInfoDisplay();
				
				// 检查是否有导入的动画包围盒数据
				const hasImportedBBoxData = this.state.animationBBoxData.isInitialized;
				
				if (!hasImportedBBoxData) {
					// 初始化动画包围盒数据系统
					this.initAnimationBBoxData();
				}
				
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
				this.update3DDataButtonState();
				this.renderInvalidate();
				
				if (this.state.currentFileData && this.state.currentFileData.isFromZip) {
					this.showMessage("ZIP file imported successfully. Textures have been loaded.", 2000);
				} else {
					this.showMessage("Model loaded successfully", 2000);
				}
			}

			// load smpl
			async loadSMPLBinFromBuffer(buffer) {
				this.loadingProgress.update("Reading SMPL header...", 86);
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
				
				this.loadingProgress.update("Extracting vertex data...", 90);
				const verts = new Float32Array(buffer, offset, numFrames * numVerts * 3);
				offset += numFrames * numVerts * 3 * 4;
				
				const faces = new Uint32Array(buffer, offset, numFaces * 3);
				
				this.state.smplData = {
					vertices: verts,
					faces: faces,
					numFrames, numVerts
				};
				
				this.loadingProgress.update("Creating mesh geometry...", 93);
				const geo = new THREE.BufferGeometry();
				geo.setAttribute('position', new THREE.BufferAttribute(verts.subarray(0, numVerts*3), 3));
				geo.setIndex(new THREE.BufferAttribute(faces, 1));
				geo.computeVertexNormals();
				
				const mat = this.createDefaultMaterial();
				this.state.smplMesh = new THREE.Mesh(geo, mat);
				this.state.smplMesh.castShadow = this.state.lights.shadowsEnabled;
				this.state.smplMesh.receiveShadow = this.state.lights.shadowsEnabled;
				
				this.scene.add(this.state.smplMesh);
				this.state.currentModel = this.state.smplMesh;
				this.state.playback.totalFrames = numFrames;
				
				this.loadingProgress.update("SMPL mesh created", 96);
			}

			// load glb
			async loadGLBFromBuffer(buffer) {
				this.loadingProgress.start("Parsing GLB data...", 95);
				
				return new Promise((resolve, reject) => {
					this.loaders.gltf.parse(buffer, '', (gltf) => {
						this.loadingProgress.update("Processing GLB model...", 98);
						
						try {
							this.processLoadedGLB(gltf);
							this.loadingProgress.stop("GLB loaded successfully");
							resolve();
						} catch (error) {
							this.loadingProgress.error("GLB processing failed");
							reject(error);
						}
						
					}, (error) => {
						this.loadingProgress.error("GLB parsing failed");
						reject(error);
					});
				});
			}

			processLoadedGLB(gltf) {
				this.state.currentFormat = 'glb';
				this.processSceneMaterials(gltf.scene);
				this.scene.add(gltf.scene); 
				this.state.currentModel = gltf.scene;
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
				
				// ============== 恢复动画包围盒数据 ==============
				if (gltf.scene.userData && gltf.scene.userData.animationBBoxData) {
					const bboxData = this.deserializeAnimationBBoxData(gltf.scene.userData.animationBBoxData);
					this.state.animationBBoxData = bboxData;
					
					// 如果已有动画包围盒数据，直接使用
					this.state.animationBBoxData.isInitialized = true;
				}
				
				// 检查场景信息
				if (gltf.scene.userData && gltf.scene.userData.sceneInfo) {
					const sceneInfo = gltf.scene.userData.sceneInfo;
					
					// 设置播放器信息
					if (sceneInfo.hasAnimation) {
						this.state.playback.totalFrames = sceneInfo.totalFrames;
						this.state.playback.fps = sceneInfo.fps || 30;
					}
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

			// load fbx
			async loadFBXFromBuffer(buffer) {
				return new Promise((resolve, reject) => {
					this.loadingProgress.update("Starting FBX parsing...", 86);
					
					try {
						this.loadingProgress.update("Parsing FBX binary data...", 90);
						const object = this.loaders.fbx.parse(buffer, '');
						
						this.loadingProgress.update("Processing FBX model...", 93);
						this.processLoadedFBX(object);
						
						this.loadingProgress.update("FBX loaded successfully", 96);
						resolve();
						
					} catch (error) {
						const errorMsg = error.message && (error.message.includes('curveNodesMap') || error.message.includes('curves')) 
							? "FBX import failed: Three.js FBXLoader does not support camera/light property animations; remove property keyframes and re-export."
							: error.message;
						
						this.loadingProgress.error('FBX parsing failed: ' + errorMsg);
						
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
				this.processSceneMaterials(object);
				this.scene.add(object); 
				this.state.currentModel = object;
				this.saveOriginalMaterials(object);
				
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

			// load obj
			async loadOBJFromBuffer(text) {
				return new Promise((resolve, reject) => {
					this.loadingProgress.update("Parsing OBJ text data...", 87);
					
					try {
						setTimeout(() => {
							this.loadingProgress.update("Creating 3D object...", 90);
							const object = this.loaders.obj.parse(text);
							
							this.loadingProgress.update("Processing OBJ model...", 93);
							this.processLoadedOBJ(object);
							
							this.loadingProgress.update("Setting up materials...", 96);
							resolve();
						}, 50);
						
					} catch (error) {
						this.loadingProgress.error('OBJ parsing failed: ' + error.message);
						reject(error);
					}
				});
			}

			processLoadedOBJ(object) {
				this.state.currentFormat = 'obj';
				this.processSceneMaterials(object);
				this.scene.add(object);
				this.state.currentModel = object;
				this.saveOriginalMaterials(object);
				this.state.playback.totalFrames = 1;
			}

			processSceneMaterials(sceneObject) {
				sceneObject.traverse(child => {
					if (child.isMesh) {
						if (!child.material) {
							child.material = this.createDefaultMaterial();
							child.userData.autoCreatedMaterial = true;
						} else {
							child.userData.autoCreatedMaterial = false;
							const materials = Array.isArray(child.material) ? child.material : [child.material];
							let needsMaterialUpdate = false;
							const convertedMaterials = [];
							
							// 修复材质属性
							// 转换standard材质，清除无效贴图链接
							materials.forEach(mat => {
								if (!mat.emissiveMap && mat.emissiveIntensity === 1) {
									mat.emissiveIntensity = 0;
								}
								if (!mat.metalnessMap && mat.metalness === 1) {
									mat.metalness = 0;
								}
								
								this.cleanupMissingTextures(mat);
								const convertedMat = this.convertPhongMaterialToStandard(mat);
								
								if (convertedMat !== mat) {
									needsMaterialUpdate = true;
								}
								
								convertedMaterials.push(convertedMat);
							});
							
							if (needsMaterialUpdate) {
								child.material = convertedMaterials.length === 1 ? convertedMaterials[0] : convertedMaterials;
							}
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
			}

			cleanupMissingTextures(material) {
				if (!material) return;
				
				// 检查所有可能的贴图属性
				const textureProperties = [
					'map', 'lightMap', 'bumpMap', 'normalMap', 'displacementMap', 
					'alphaMap', 'emissiveMap', 'metalnessMap', 'roughnessMap', 
					'aoMap', 'envMap', 'specularMap'
				];
				
				textureProperties.forEach(prop => {
					if (material[prop] && material[prop].isTexture) {
						const texture = material[prop];
						
						// 检查贴图是否有效
						if (!texture.image || 
							texture.image.width === 0 || 
							texture.image.height === 0 ||
							(texture.image.src && texture.image.src.includes('undefined'))) {
							
							material[prop] = null;
							
							// 如果是alphaMap被移除，确保材质不是透明的
							if (prop === 'alphaMap' && material.transparent) {
								material.transparent = false;
								material.opacity = 1.0;
							}
						}
					}
				});
			}

			convertPhongMaterialToStandard(material) {
				if (!material) return null;
				
				const materialId = material.uuid;
				
				// 1. 检查缓存
				if (this.materialConversionCache.has(materialId)) {
					return this.materialConversionCache.get(materialId);
				}
				
				// 2. 检查是否为需要转换的材质
				const isPhong = material.isMeshPhongMaterial || 
								material.type === 'MeshPhongMaterial' ||
								(material.userData && material.userData.isOriginalPhong);
				
				if (!isPhong) {
					// 不是Phong材质，无需转换，返回原材质
					// 不缓存非Phong材质，因为原材质应该被复用
					return material;
				}
				
				// 记录原始信息
				const originalInfo = {
					type: material.type,
					shininess: material.shininess,
					specular: material.specular ? material.specular.clone() : null,
					color: material.color ? material.color.clone() : null,
					emissive: material.emissive ? material.emissive.clone() : null
				};
				
				// 创建Standard材质
				const standardMaterial = new THREE.MeshStandardMaterial();
				
				// 复制通用属性
				standardMaterial.name = material.name || 'Converted_' + Math.random().toString(36).substr(2, 9);
				
				// 颜色和贴图
				if (material.color) standardMaterial.color.copy(material.color);
				if (material.emissive) standardMaterial.emissive.copy(material.emissive);
				standardMaterial.emissiveIntensity = material.emissiveIntensity || 0;
				
				// 复制所有贴图
				this.copyTexturesToStandardMaterial(material, standardMaterial);
				
				// 透明度相关
				standardMaterial.transparent = material.transparent;
				standardMaterial.opacity = material.opacity || 1.0;
				standardMaterial.alphaTest = material.alphaTest;
				standardMaterial.depthWrite = material.depthWrite !== undefined ? material.depthWrite : true;
				standardMaterial.side = material.side || THREE.FrontSide;
				
				// ============ 智能属性转换 ============
				
				// 1. 将shininess转换为roughness
				if (material.shininess !== undefined) {
					const shininess = material.shininess;
					let roughness = 1.0;
					
					if (shininess > 0) {
						// 非线性转换
						const normalizedShininess = Math.min(shininess / 1000, 1.0);
						roughness = 1.0 - Math.sqrt(normalizedShininess);
						
						// 限制范围
						roughness = Math.max(0.04, Math.min(roughness, 1.0));
						
						// 对于高shininess，进一步降低roughness
						if (shininess > 500) {
							roughness = Math.min(roughness, 0.15);
						}
					}
					
					standardMaterial.roughness = roughness;
				} else {
					standardMaterial.roughness = 0.5;
				}
				
				// 2. 根据specular颜色设置metalness
				if (material.specular) {
					const specular = material.specular;
					const specularIntensity = (specular.r + specular.g + specular.b) / 3;
					
					if (specularIntensity > 0.9) {
						// 非常高的specular，很可能是金属
						standardMaterial.metalness = 0.9;
						standardMaterial.roughness = Math.min(standardMaterial.roughness, 0.2);
					} else if (specularIntensity > 0.7) {
						// 高specular，可能是抛光金属
						standardMaterial.metalness = 0.7;
						standardMaterial.roughness = Math.min(standardMaterial.roughness, 0.3);
					} else if (specularIntensity > 0.4) {
						// 中等specular
						standardMaterial.metalness = 0.3;
					} else if (specularIntensity > 0.1) {
						// 低specular，非金属但有一定光泽
						standardMaterial.metalness = 0.0;
						standardMaterial.roughness = Math.min(standardMaterial.roughness, 0.7);
					} else {
						// 非常低的specular，哑光材质
						standardMaterial.metalness = 0.0;
						standardMaterial.roughness = Math.max(standardMaterial.roughness, 0.8);
					}
					
					// 保存specular信息
					standardMaterial.userData = standardMaterial.userData || {};
					standardMaterial.userData.originalSpecularIntensity = specularIntensity;
				} else {
					// 没有specular，默认为非金属
					standardMaterial.metalness = 0.0;
				}
				
				// 其他属性
				standardMaterial.wireframe = material.wireframe;
				standardMaterial.wireframeLinewidth = material.wireframeLinewidth;
				standardMaterial.flatShading = material.flatShading;
				
				// 保存原始Phong信息
				standardMaterial.userData = standardMaterial.userData || {};
				standardMaterial.userData.convertedFromPhong = true;
				standardMaterial.userData.originalShininess = originalInfo.shininess;
				standardMaterial.userData.originalSpecular = originalInfo.specular;
				standardMaterial.userData.originalMaterialType = originalInfo.type;
				
				// 缓存转换后的材质
				this.materialConversionCache.set(materialId, standardMaterial);
				
				return standardMaterial;
			}

			copyTexturesToStandardMaterial(sourceMaterial, targetMaterial) {
				const textureProperties = [
					'map', 'aoMap', 'emissiveMap', 'bumpMap', 'normalMap',
					'displacementMap', 'roughnessMap', 'metalnessMap',
					'alphaMap', 'envMap', 'lightMap'
				];
				
				textureProperties.forEach(prop => {
					if (sourceMaterial[prop] && sourceMaterial[prop].isTexture) {
						targetMaterial[prop] = sourceMaterial[prop];
						
						// 复制贴图参数
						if (sourceMaterial[prop + 'Intensity'] !== undefined) {
							targetMaterial[prop + 'Intensity'] = sourceMaterial[prop + 'Intensity'];
						}
						
						if (prop === 'normalMap' && sourceMaterial.normalScale) {
							targetMaterial.normalScale = sourceMaterial.normalScale.clone();
						}
						
						if (prop === 'bumpMap' && sourceMaterial.bumpScale !== undefined) {
							targetMaterial.bumpScale = sourceMaterial.bumpScale;
						}
						
						if (prop === 'displacementMap' && sourceMaterial.displacementScale !== undefined) {
							targetMaterial.displacementScale = sourceMaterial.displacementScale;
						}
					}
				});
			}

			// load ply
			async loadPLYFromBuffer(buffer) {
				return new Promise((resolve, reject) => {
					try { 
						this.loadingProgress.update("Parsing PLY binary data...", 87);
						
						setTimeout(() => {
							this.updateLoadingProgress(97, "Parsing PLY data...");
							const geometry = this.loaders.ply.parse(buffer);
							
							// 检查顶点颜色属性
							this.loadingProgress.update("Checking vertex attributes...", 90);
							const hasVertexColors = geometry.attributes.color !== undefined;
							const hasNormals = geometry.attributes.normal !== undefined;
							
							// 如果没有法线，计算顶点法线（对于网格）
							if (!hasNormals) {
								geometry.computeVertexNormals();
							}
							
							// 检查几何体类型（点云或网格）
							this.loadingProgress.update("Creating mesh...", 93);
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
							
							this.loadingProgress.update("PLY mesh created", 96);
							resolve();
							
						}, 50);
						
					} catch (error) {
						this.loadingProgress.error('PLY parsing failed: ' + error.message);
						reject(error);
					}
				});
			}

			// load zip
			async loadZipDataFromBuffer(buffer) {
				let virtualFS = null;
				
				try {
					this.loadingProgress.update("Loading ZIP data...", 86);
					const zip = await this.JSZip.loadAsync(buffer);
					
					// 记录ZIP内容
					/* this.loadingProgress.update("Analyzing ZIP contents...", 88); */
					/* this.logZipContents(zip); */
					
					// 分析ZIP内容，确定格式
					const format = this.detectZipFormat(zip);
					
					if (!format) {
						throw new Error('Cannot find supported 3D model format in ZIP');
					}
					
					this.loadingProgress.update('Detected format: ' + format.type.toUpperCase() + ', main file: ' + format.mainFile, 90);
					
					// 创建临时虚拟文件系统
					this.loadingProgress.update("Creating virtual file system...", 92);
					virtualFS = new ZipVirtualFileSystem(zip);
					
					// 设置当前活动的虚拟文件系统
					this.currentVirtualFS = virtualFS;
					this.currentZipMainFile = format.mainFile;
					
					// 根据格式调用相应的加载器
					this.loadingProgress.update('Loading ' + format.type.toUpperCase() + ' from ZIP...', 94);
					switch(format.type) {
						case 'glb':
							await this.loadGLBFromZip(zip, format.mainFile, virtualFS);
							break;
						case 'fbx':
							await this.loadFBXFromZip(zip, format.mainFile, virtualFS);
							break;
						case 'obj':
							await this.loadOBJFromZip(zip, format.mainFile, virtualFS);
							break;
						default:
							throw new Error('Unsupported format: ' + format.type);
					}
					
					this.loadingProgress.update("ZIP processing complete", 98);
					
				} catch (error) {
					this.loadingProgress.error('ZIP parsing error: ' + error.message);
					throw error;
				} finally {
					// 清理：恢复全局纹理加载并清理虚拟文件系统
					this.currentVirtualFS = null;
					this.currentZipMainFile = null;
					
					if (virtualFS) {
						virtualFS.dispose();
					}
				}
			}

			logZipContents(zip) {
				console.log("ZIP Content:");
				const files = Object.keys(zip.files);
				const categories = {
					models: [],
					textures: [],
					materials: [],
					others: []
				};
				
				files.forEach(file => {
					const ext = file.split('.').pop().toLowerCase();
					if (['obj', 'fbx', 'glb', 'ply'].includes(ext)) {
						categories.models.push(file);
					} else if (['png', 'jpg', 'jpeg', 'tga', 'bmp', 'tiff', 'webm'].includes(ext)) {
						categories.textures.push(file);
					} else if (['mtl'].includes(ext)) {
						categories.materials.push(file);
					} else {
						categories.others.push(file);
					}
				});
				
				console.log("  Model: " + categories.models.length);
				categories.models.forEach(f => console.log("    " + f));
				
				console.log("  Texture: " + categories.textures.length);
				categories.textures.forEach(f => console.log("    " + f));
				
				console.log("  Material: " + categories.materials.length);
				categories.materials.forEach(f => console.log("    " + f));
				
				console.log("  Other: " + categories.others.length);
				categories.others.forEach(f => console.log("    " + f));
			}

			detectZipFormat(zip) {
				const files = Object.keys(zip.files);
				
				const formatPriority = [
					{ ext: 'glb', type: 'glb' },
					{ ext: 'gltf', type: 'glb' },
					{ ext: 'fbx', type: 'fbx' },
					{ ext: 'obj', type: 'obj' }
				];
				
				for (const format of formatPriority) {
					const found = files.find(file => 
						file.toLowerCase().endsWith('.' + format.ext)
					);
					
					if (found) {
						if (format.ext === 'obj') {
							const baseName = found.replace(/\.obj$/i, '');
							
							const possibleMtlNames = [
								baseName + '.mtl',
								baseName.replace(/[_-].*$/, '') + '.mtl',
								'material.mtl',
								'model.mtl'
							];
							
							let mtlFile = null;
							for (const mtlName of possibleMtlNames) {
								if (files.find(f => f.toLowerCase() === mtlName.toLowerCase())) {
									mtlFile = mtlName;
									break;
								}
							}
							
							return {
								type: format.type,
								mainFile: found,
								mtlFile: mtlFile
							};
						}
						
						return {
							type: format.type,
							mainFile: found
						};
					}
				}
				
				return null;
			}

			// load glb zip
			async loadGLBFromZip(zip, mainFilePath, virtualFS) {
				try {
					this.loadingProgress.start("Loading GLB/GLTF from ZIP...", 95);
					
					// 检查文件扩展名
					const ext = mainFilePath.toLowerCase().split('.').pop();
					const isGLTF = ext === 'gltf';
					
					let gltf;
					
					if (isGLTF) {
						// 1. 读取 GLTF JSON 文件
						this.loadingProgress.update("Reading GLTF JSON file...", 96);
						const gltfText = await virtualFS.getText(mainFilePath);
						const gltfJson = JSON.parse(gltfText);
						
						// 2. 处理分离式 GLTF 资源
						this.loadingProgress.update("Processing external resources...", 97);
						await this.processSeparatedGLTFResources(gltfJson, mainFilePath, virtualFS);
						
						// 3. 使用 GLTFLoader 解析处理后的 JSON
						this.loadingProgress.update("Parsing GLTF data...", 98);
						gltf = await this.parseGLTFJsonWithLoader(gltfJson, mainFilePath, virtualFS);
						
					} else {
						// GLB文件也需要当作分离式处理
						this.loadingProgress.update("Reading GLB data...", 96);
						const arrayBuffer = await virtualFS.getArrayBuffer(mainFilePath);
						
						// 将 GLB 转换为 GLTF JSON 进行处理
						this.loadingProgress.update("Converting GLB to GLTF...", 97);
						const gltfJson = await this.extractGLTFJsonFromGLB(arrayBuffer);
						
						// 处理分离式 GLTF 资源
						this.loadingProgress.update("Processing external resources...", 98);
						await this.processSeparatedGLTFResources(gltfJson, mainFilePath, virtualFS);
						
						// 使用 GLTFLoader 解析
						gltf = await this.parseGLTFJsonWithLoader(gltfJson, mainFilePath, virtualFS);
					}
					
					// 使用现有的处理函数
					this.loadingProgress.update("Finalizing model...", 99);
					this.processLoadedGLB(gltf);
					
					// 更新状态
					this.state.currentFormat = isGLTF ? 'gltf' : 'glb';
					this.state.currentFileData = { 
						filename: mainFilePath, 
						format: isGLTF ? 'gltf' : 'glb',
						isFromZip: true
					};
					
					this.loadingProgress.stop((isGLTF ? "GLTF" : "GLB") + " from ZIP loaded successfully", 100);
					
				} catch (error) {
					this.loadingProgress.error("Failed to load from ZIP: " + error.message);
					throw error;
				} finally {
					// 清理虚拟文件系统
					if (virtualFS) {
						virtualFS.dispose();
					}
				}
			}

			async extractGLTFJsonFromGLB(arrayBuffer) {
				// GLB 格式解析
				const dataView = new DataView(arrayBuffer);
				
				// 检查魔数
				const magic = dataView.getUint32(0, true);
				if (magic !== 0x46546C67) { // "glTF" 的 ASCII
					throw new Error('Invalid GLB file: wrong magic number');
				}
				
				// 获取版本
				const version = dataView.getUint32(4, true);
				
				// 获取长度
				const length = dataView.getUint32(8, true);
				
				// 解析第一个 Chunk（应该是 JSON）
				const chunkLength = dataView.getUint32(12, true);
				const chunkType = dataView.getUint32(16, true);
				
				if (chunkType !== 0x4E4F534A) { // "JSON" 的 ASCII
					throw new Error('Invalid GLB file: first chunk is not JSON');
				}
				
				// 提取 JSON 数据
				const jsonStart = 20;
				const jsonEnd = jsonStart + chunkLength;
				const jsonBytes = new Uint8Array(arrayBuffer, jsonStart, chunkLength);
				const jsonText = new TextDecoder().decode(jsonBytes);
				const gltfJson = JSON.parse(jsonText);
				
				return gltfJson;
			}

			async processSeparatedGLTFResources(gltfJson, mainFilePath, virtualFS) {
				const baseDir = mainFilePath.substring(0, mainFilePath.lastIndexOf('/') + 1);
				
				// 1. 处理 buffers (BIN 文件)
				if (gltfJson.buffers && Array.isArray(gltfJson.buffers)) {
					for (let i = 0; i < gltfJson.buffers.length; i++) {
						const buffer = gltfJson.buffers[i];
						
						if (buffer.uri && !buffer.uri.startsWith('data:')) {
							try {
								// 构建完整路径
								const bufferPath = PathUtils.cleanPath(buffer.uri);
								const fullBufferPath = PathUtils.joinPaths(baseDir, bufferPath);
								
								// 从ZIP中读取BIN文件
								const arrayBuffer = await virtualFS.getArrayBuffer(fullBufferPath);
								
								// 转换为base64 Data URI
								const base64 = this.arrayBufferToBase64(arrayBuffer);
								buffer.uri = 'data:application/octet-stream;base64,' + base64;
							} catch (error) {
								console.log('Failed to load buffer: ' + buffer.uri, error);
								throw new Error('Failed to load buffer: ' + buffer.uri);
							}
						}
					}
				}
				
				// 2. 处理 images (纹理)
				if (gltfJson.images && Array.isArray(gltfJson.images)) {
					const texturePromises = [];
					
					for (let i = 0; i < gltfJson.images.length; i++) {
						const image = gltfJson.images[i];
						
						if (image.uri && !image.uri.startsWith('data:') && !image.uri.startsWith('blob:')) {
							const texturePromise = (async () => {
								try {
									// 构建完整路径
									const imagePath = PathUtils.cleanTexturePath(image.uri);
									const fullImagePath = PathUtils.joinPaths(baseDir, imagePath);
									
									// 从ZIP中获取纹理的Blob URL
									const blobUrl = await virtualFS.getBlobUrl(fullImagePath, mainFilePath);
									
									// 更新图像URI为Blob URL
									image.uri = blobUrl;
								} catch (error) {
									// 如果纹理加载失败，尝试其他可能的位置
									const fileName = PathUtils.getFileName(image.uri);
									try {
										const blobUrl = await virtualFS.getBlobUrl(fileName, mainFilePath);
										image.uri = blobUrl;
										console.log('Find texture using filename: ' + fileName);
									} catch (e) {
										console.log('Failed to load texture: ' + image.uri);
									}
								}
							})();
							
							texturePromises.push(texturePromise);
						}
					}
					
					// 等待所有纹理处理完成
					await Promise.all(texturePromises);
				}
			}

			parseGLTFJsonWithLoader(gltfJson, mainFilePath, virtualFS) {
				return new Promise((resolve, reject) => {
					try {
						// 创建 GLTFLoader
						const gltfLoader = new GLTFLoader();
						
						// 设置自定义文件加载器（如果需要）
						// 注意：有些Three.js版本可能没有setResourceLoader方法
						// 所以我们可以通过重写FileLoader来实现
						
						// 方法1：使用现有的 THREE.FileLoader
						const fileLoader = new THREE.FileLoader();
						fileLoader.setResponseType('arraybuffer');
						
						// 方法2：如果GLTFLoader支持设置manager，我们可以自定义LoadingManager
						const loadingManager = new THREE.LoadingManager();
						
						// 设置URL修改器，将相对路径转换为blob URL
						loadingManager.setURLModifier((url) => {
							// 如果是data URI或blob URL，直接返回
							if (url.startsWith('data:') || url.startsWith('blob:')) {
								return url;
							}
							
							// 构建完整路径
							const baseDir = mainFilePath.substring(0, mainFilePath.lastIndexOf('/') + 1);
							const fullPath = PathUtils.joinPaths(baseDir, url);
							
							// 尝试从虚拟文件系统获取Blob URL
							return virtualFS.getBlobUrl(fullPath, mainFilePath).catch(() => {
								return url;
							});
						});
						
						// 创建使用自定义manager的GLTFLoader
						const gltfLoaderWithManager = new GLTFLoader(loadingManager);
						
						// 将GLTF JSON转换为字符串
						const gltfJsonString = JSON.stringify(gltfJson);
						
						// 使用parse方法解析GLTF JSON
						gltfLoaderWithManager.parse(gltfJsonString, '', (gltf) => {
							resolve(gltf);
						}, (error) => {
							// 如果带manager的加载器失败，尝试普通加载器
							gltfLoader.parse(gltfJsonString, '', (gltf) => {
								resolve(gltf);
							}, (secondError) => {
								reject(secondError);
							});
						});
						
					} catch (error) {
						console.log('Parse GLTF error:', error);
						reject(error);
					}
				});
			}

			arrayBufferToBase64(buffer) {
				let binary = '';
				const bytes = new Uint8Array(buffer);
				const len = bytes.byteLength;
				for (let i = 0; i < len; i++) {
					binary += String.fromCharCode(bytes[i]);
				}
				return window.btoa(binary);
			}

			// load fbx zip
			async loadFBXFromZip(zip, mainFilePath, virtualFS) {
				try {
					this.loadingProgress.start("Extracting FBX from ZIP...", 95);
					
					// 1. 获取FBX文件的ArrayBuffer
					this.loadingProgress.update("Reading FBX data...", 96);
					const arrayBuffer = await virtualFS.getArrayBuffer(mainFilePath);
					
					// 2. 使用映射提取器获取材质-贴图对应关系
					this.loadingProgress.update("Extracting texture mappings...", 97);
					const mappingExtractor = new FBXMappingExtractor();
					const materialTextureMap = mappingExtractor.extractFromBuffer(arrayBuffer);
					
					// 3. 使用官方FBXLoader加载FBX
					this.loadingProgress.update("Parsing FBX model...", 98);
					const object = this.loaders.fbx.parse(arrayBuffer, '');
					
					// 4. 保存映射关系到状态中
					this.state.fbxTextureMapping = materialTextureMap;
					
					if (materialTextureMap.size > 0) {
						// 5. 使用映射关系处理纹理
						this.loadingProgress.update("Processing textures with mapping...");
						await this.processFBXTexturesWithMapping(object, mainFilePath, virtualFS, materialTextureMap);
					} else {
						// 6. 如果没有映射关系，使用默认处理
						this.loadingProgress.update("Processing textures (fallback)...");
						await this.processFBXTexturesFallback(object, mainFilePath, virtualFS);
					}
					
					// 7. 使用现有的处理函数
					this.loadingProgress.update("Finalizing model...");
					this.processLoadedFBX(object);
					
					// 更新状态
					this.state.currentFormat = 'fbx';
					this.state.currentFileData = { 
						filename: mainFilePath, 
						format: 'fbx',
						isFromZip: true
					};
					
					this.loadingProgress.stop("FBX from ZIP loaded successfully");
					
				} catch (error) {
					this.loadingProgress.error("Failed to load FBX from ZIP");
					throw error;
				}
			}

			async processFBXTexturesWithMapping(object, mainFilePath, virtualFS, materialTextureMap) {
				if (!materialTextureMap || materialTextureMap.size === 0) {
					return this.processFBXTexturesFallback(object, mainFilePath, virtualFS);
				}
				
				// 创建纹理加载器
				this.loadingProgress.update("Setting up texture loader...");
				const textureLoader = new TextureLoaderFromZip(virtualFS);
				
				// 收集所有材质
				const materials = new Map();
				
				object.traverse(child => {
					if (child.isMesh && child.material) {
						const materialArray = Array.isArray(child.material) ? child.material : [child.material];
						materialArray.forEach(mat => {
							if (mat && mat.name) {
								materials.set(mat.name, mat);
							}
						});
					}
				});
				
				// 为每个材质应用贴图
				const texturePromises = [];
				const totalTextures = Array.from(materialTextureMap.values()).reduce((sum, mappings) => sum + mappings.size, 0);
				
				this.loadingProgress.update('Processing ' + totalTextures + ' textures...');
				
				for (const [materialName, textureMappings] of materialTextureMap.entries()) {
					const material = materials.get(materialName);
					
					if (!material) {
						continue;
					}
					
					// 为每个纹理类型加载并应用贴图
					for (const [threeJsProp, textureInfo] of textureMappings.entries()) {
						try {
							// 获取贴图文件名
							let textureFileName = textureInfo.imageFilename;
							if (!textureFileName) {
								continue;
							}
							
							// 从ZIP中加载贴图
							const promise = textureLoader.loadTexture(textureFileName, {
								basePath: mainFilePath,
								textureType: threeJsProp
							}).then(texture => {
								if (texture) {
									// 应用贴图到材质
									material[threeJsProp] = texture;
									
									// 设置材质属性
									this.setMaterialPropertiesForTexture(material, threeJsProp);
									
									material.needsUpdate = true;
									
								}
							}).catch(error => {
								console.log('Process ' + threeJsProp + ' of ' + materialName + ' error:', error);
							});
							
							texturePromises.push(promise);
							
						} catch (error) {
							console.log('Process ' + threeJsProp + ' of ' + materialName + ' error:', error);
						}
					}
				}
				
				// 等待所有纹理加载完成
				if (texturePromises.length > 0) {
					await Promise.allSettled(texturePromises);
					this.loadingProgress.update(texturePromises.length + ' textures loaded...');
				}
			}

			async processFBXTexturesFallback(object, mainFilePath, virtualFS) {
				// 创建纹理加载器
				const textureLoader = new TextureLoaderFromZip(virtualFS);
				
				// 收集所有需要处理的纹理
				const texturePromises = [];
				
				object.traverse(child => {
					if (child.isMesh && child.material) {
						const materials = Array.isArray(child.material) ? child.material : [child.material];
						
						materials.forEach((material, matIndex) => {
							if (!material) return;
							
							// 检查各种可能的纹理属性
							const textureProps = [
								'map', 'normalMap', 'roughnessMap', 'metalnessMap',
								'emissiveMap', 'alphaMap', 'aoMap', 'displacementMap',
								'specularMap', 'bumpMap'
							];
							
							textureProps.forEach(prop => {
								const texture = material[prop];
								if (texture && texture.image && texture.image.src) {
									const src = texture.image.src;
									
									// 如果是外部纹理，尝试从ZIP加载
									if (!src.startsWith('data:') && !src.startsWith('blob:')) {
										const fileName = PathUtils.cleanTextureUrl(src);
										
										if (fileName) {
											const promise = textureLoader.loadTexture(fileName, {
												basePath: mainFilePath,
												textureType: prop
											}).then(newTexture => {
												if (newTexture) {
													material[prop] = newTexture;
													material.needsUpdate = true;
												}
											}).catch(error => {
												console.log('Load texture failed:', fileName, error);
											});
											
											texturePromises.push(promise);
										}
									}
								}
							});
						});
					}
				});
				
				// 等待所有纹理加载完成
				if (texturePromises.length > 0) {
					await Promise.allSettled(texturePromises);
				}
			}

			setMaterialPropertiesForTexture(material, textureType) {
				switch(textureType) {
					case 'map':
						// 基础贴图，不需要额外设置
						break;
					case 'normalMap':
						material.normalScale = new THREE.Vector2(1, 1);
						break;
					case 'roughnessMap':
						material.roughness = material.roughness || 1.0;
						break;
					case 'metalnessMap':
						material.metalness = material.metalness || 0.0;
						break;
					case 'emissiveMap':
						material.emissiveIntensity = material.emissiveIntensity || 1.0;
						break;
					case 'alphaMap':
						material.transparent = true;
						break;
					case 'aoMap':
						material.aoMapIntensity = material.aoMapIntensity || 1.0;
						break;
					case 'bumpMap':
						material.bumpScale = material.bumpScale || 1.0;
						break;
				}
			}

			// load obj zip
			async loadOBJFromZip(zip, mainFilePath, virtualFS) {
				try {
					const formatInfo = this.detectZipFormat(zip);
					
					this.loadingProgress.start("Extracting OBJ from ZIP...", 95);
					
					// 加载OBJ文件
					this.loadingProgress.update("Reading OBJ file...", 96);
					const objText = await virtualFS.getText(mainFilePath);
					
					// 如果有MTL文件，加载它
					let materialsDict = null;
					if (formatInfo.mtlFile) {
						try {
							this.loadingProgress.update("Loading MTL materials...", 97);
							const mtlText = await virtualFS.getText(formatInfo.mtlFile);
							materialsDict = await this.loadMTLFromZip(mtlText, formatInfo.mtlFile, virtualFS);
							
						} catch (mtlError) {
							materialsDict = null;
						}
					}
					
					// 分析OBJ文件，判断是否全部是单材质物体
					this.loadingProgress.update("Analyzing OBJ structure...", 98);
					const allSingleMaterial = this.isAllObjSingleMaterial(objText);
					
					let object;
					if (allSingleMaterial) {
						this.loadingProgress.update("Parsing OBJ (single material)...");
						object = await this.loadSingleMaterialOBJ(objText, materialsDict);
					} else {
						this.loadingProgress.update("Parsing OBJ (multi-material)...");
						object = await this.parseOBJManually(objText, mainFilePath, virtualFS, materialsDict);
					}
					
					// 使用现有的处理函数
					this.loadingProgress.update("Finalizing OBJ model...");
					this.processLoadedOBJ(object, materialsDict, mainFilePath);
					
					// 更新状态
					this.state.currentFormat = 'obj';
					this.state.currentFileData = { 
						filename: mainFilePath, 
						format: 'obj',
						isFromZip: true
					};
					
					this.loadingProgress.stop("OBJ from ZIP loaded successfully");
					return object;
					
				} catch (error) {
					this.loadingProgress.error("Failed to load OBJ from ZIP");
					throw error;
				}
			}

			isAllObjSingleMaterial(objText) {
				const lines = objText.split('\\n');
				let currentMaterials = new Set();
				let hasMultiMaterialObject = false;
				let inObject = false;
				
				for (let i = 0; i < lines.length; i++) {
					const line = lines[i].trim();
					if (!line || line.startsWith('#')) continue;
					
					const parts = line.split(/\\s+/);
					const keyword = parts[0];
					
					if (keyword === 'o' || keyword === 'g') {
						// 新物体开始，检查前一个物体的材质数量
						if (inObject && currentMaterials.size > 1) {
							hasMultiMaterialObject = true;
							break;
						}
						currentMaterials.clear();
						inObject = true;
					} else if (keyword === 'usemtl') {
						if (parts.length > 1) {
							currentMaterials.add(parts[1]);
							if (currentMaterials.size > 1) {
								hasMultiMaterialObject = true;
								break;
							}
						}
					}
				}
				
				// 检查最后一个物体
				if (!hasMultiMaterialObject && inObject && currentMaterials.size > 1) {
					hasMultiMaterialObject = true;
				}
				
				return !hasMultiMaterialObject;
			}

			async loadSingleMaterialOBJ(objText, materialsDict) {
				// 与obj-singlemat.js完全相同的方法
				const objLoader = new OBJLoader();
				const object = objLoader.parse(objText);
				
				// 手动应用材质到网格
				if (materialsDict) {
					this.applyMaterialsToOBJ(object, materialsDict);
				}
				
				return object;
			}

			applyMaterialsToOBJ(object, materialsDict) {
				object.traverse(function(child) {
					if (child.isMesh && child.material) {
						// 获取材质名称
						let materialName = null;
						
						// 尝试从不同地方获取材质名称
						if (child.material.name && child.material.name !== '') {
							materialName = child.material.name;
						} else if (child.userData && child.userData.materialName) {
							materialName = child.userData.materialName;
						} else {
							// 如果没有材质名，使用默认
							materialName = 'defaultMat';
						}
						
						// 从材质字典中获取对应的Three.js材质
						if (materialsDict[materialName]) {
							child.material = materialsDict[materialName];
						} else {
							// 如果没有找到对应材质，使用第一个可用材质
							const firstMaterialName = Object.keys(materialsDict)[0];
							if (firstMaterialName) {
								child.material = materialsDict[firstMaterialName];
							}
						}
					}
				}.bind(this));
			}

			async parseOBJManually(objText, mainFilePath, virtualFS, materialsDict) {
				try {
					const startTime = performance.now();
					
					this.loadingProgress.update("Starting OBJ parsing...", 98);
					
					// ============== 官方OBJLoader的核心算法复制 ==============
					
					// 复制官方OBJLoader使用的常量和辅助函数
					const _object_pattern = /^[og]\\s*(.+)?/;
					const _material_library_pattern = /^mtllib /;
					const _material_use_pattern = /^usemtl /;
					const _face_vertex_data_separator_pattern = /\\s+/;
					
					// 解析状态类（完全复制官方OBJLoader的ParserState逻辑）
					class ParserState {
						constructor() {
							this.objects = [];
							this.object = {};
							this.vertices = [];
							this.normals = [];
							this.colors = [];
							this.uvs = [];
							this.materials = {};
							this.materialLibraries = [];
							
							// 启动第一个对象
							this.startObject("", false);
						}
						
						startObject(name, fromDeclaration = false) {
							// 启用会导致所有物体合成一个物体
							/* if (this.object && this.object.fromDeclaration === false) {
								this.object.name = name;
								this.object.fromDeclaration = (fromDeclaration !== false);
								return;
							} */
							
							const previousMaterial = (this.object && typeof this.object.currentMaterial === 'function') 
								? this.object.currentMaterial() 
								: undefined;
							
							if (this.object && this.object._finalize) {
								this.object._finalize(true);
							}
							
							const newObject = {
								name: name || "",
								fromDeclaration: (fromDeclaration !== false),
								geometry: {
									vertices: [],
									normals: [],
									colors: [],
									uvs: [],
									hasUVIndices: false
								},
								materials: [],
								smooth: true,
								
								startMaterial: function(name, libraries) {
									const previous = this._finalize(false);
									
									// 新的usemtl声明覆盖继承的材质
									if (previous && (previous.inherited || previous.groupCount <= 0)) {
										this.materials.splice(previous.index, 1);
									}
									
									const material = {
										index: this.materials.length,
										name: name || "",
										mtllib: (Array.isArray(libraries) && libraries.length > 0 ? libraries[libraries.length - 1] : ""),
										smooth: (previous !== undefined ? previous.smooth : this.smooth),
										groupStart: (previous !== undefined ? previous.groupEnd : 0),
										groupEnd: -1,
										groupCount: -1,
										inherited: false
									};
									
									this.materials.push(material);
									return material;
								},
								
								currentMaterial: function() {
									if (this.materials.length > 0) {
										return this.materials[this.materials.length - 1];
									}
									return undefined;
								},
								
								_finalize: function(end) {
									const lastMultiMaterial = this.currentMaterial();
									if (lastMultiMaterial && lastMultiMaterial.groupEnd === -1) {
										lastMultiMaterial.groupEnd = this.geometry.vertices.length / 3;
										lastMultiMaterial.groupCount = lastMultiMaterial.groupEnd - lastMultiMaterial.groupStart;
										lastMultiMaterial.inherited = false;
									}
									
									// 忽略尾部没有面的材质
									if (end && this.materials.length > 1) {
										for (let mi = this.materials.length - 1; mi >= 0; mi--) {
											if (this.materials[mi].groupCount <= 0) {
												this.materials.splice(mi, 1);
											}
										}
									}
									
									// 确保至少有一个空材质
									if (end && this.materials.length === 0) {
										this.materials.push({
											name: "",
											smooth: this.smooth
										});
									}
									
									return lastMultiMaterial;
								}
							};
							
							// 继承前一个对象的材质
							if (previousMaterial && previousMaterial.name) {
								const declared = {
									index: 0,
									name: previousMaterial.name,
									mtllib: previousMaterial.mtllib,
									smooth: previousMaterial.smooth,
									groupStart: 0,
									groupEnd: -1,
									groupCount: -1,
									inherited: true
								};
								newObject.materials.push(declared);
							}
							
							this.object = newObject;
							this.objects.push(this.object);
						}
						
						finalize() {
							if (this.object && this.object._finalize) {
								this.object._finalize(true);
							}
						}
						
						parseVertexIndex(value, len) {
							const index = parseInt(value, 10);
							return (index >= 0 ? index - 1 : index + len / 3) * 3;
						}
						
						parseNormalIndex(value, len) {
							const index = parseInt(value, 10);
							return (index >= 0 ? index - 1 : index + len / 3) * 3;
						}
						
						parseUVIndex(value, len) {
							const index = parseInt(value, 10);
							return (index >= 0 ? index - 1 : index + len / 2) * 2;
						}
						
						addVertex(a, b, c) {
							const src = this.vertices;
							const dst = this.object.geometry.vertices;
							dst.push(src[a], src[a + 1], src[a + 2]);
							dst.push(src[b], src[b + 1], src[b + 2]);
							dst.push(src[c], src[c + 1], src[c + 2]);
						}
						
						addNormal(a, b, c) {
							const src = this.normals;
							const dst = this.object.geometry.normals;
							dst.push(src[a], src[a + 1], src[a + 2]);
							dst.push(src[b], src[b + 1], src[b + 2]);
							dst.push(src[c], src[c + 1], src[c + 2]);
						}
						
						addUV(a, b, c) {
							const src = this.uvs;
							const dst = this.object.geometry.uvs;
							dst.push(src[a], src[a + 1]);
							dst.push(src[b], src[b + 1]);
							dst.push(src[c], src[c + 1]);
						}
						
						addDefaultUV() {
							const dst = this.object.geometry.uvs;
							dst.push(0, 0);
							dst.push(0, 0);
							dst.push(0, 0);
						}
						
						addFace(a, b, c, ua, ub, uc, na, nb, nc) {
							const vLen = this.vertices.length;
							let ia = this.parseVertexIndex(a, vLen);
							let ib = this.parseVertexIndex(b, vLen);
							let ic = this.parseVertexIndex(c, vLen);
							
							this.addVertex(ia, ib, ic);
							
							// 法线
							if (na !== undefined && na !== "") {
								const nLen = this.normals.length;
								ia = this.parseNormalIndex(na, nLen);
								ib = this.parseNormalIndex(nb, nLen);
								ic = this.parseNormalIndex(nc, nLen);
								this.addNormal(ia, ib, ic);
							} else {
								// 计算面法线
								this.addFaceNormal(ia, ib, ic);
							}
							
							// UV
							if (ua !== undefined && ua !== "") {
								const uvLen = this.uvs.length;
								ia = this.parseUVIndex(ua, uvLen);
								ib = this.parseUVIndex(ub, uvLen);
								ic = this.parseUVIndex(uc, uvLen);
								this.addUV(ia, ib, ic);
								this.object.geometry.hasUVIndices = true;
							} else {
								this.addDefaultUV();
							}
						}
						
						addFaceNormal(a, b, c) {
							const src = this.vertices;
							const dst = this.object.geometry.normals;
							
							// 计算面法线
							const x0 = src[a];
							const y0 = src[a + 1];
							const z0 = src[a + 2];
							
							const x1 = src[b];
							const y1 = src[b + 1];
							const z1 = src[b + 2];
							
							const x2 = src[c];
							const y2 = src[c + 1];
							const z2 = src[c + 2];
							
							const pA = {x: x0, y: y0, z: z0};
							const pB = {x: x1, y: y1, z: z1};
							const pC = {x: x2, y: y2, z: z2};
							
							const cb = {
								x: pC.x - pB.x,
								y: pC.y - pB.y,
								z: pC.z - pB.z
							};
							
							const ab = {
								x: pA.x - pB.x,
								y: pA.y - pB.y,
								z: pA.z - pB.z
							};
							
							const normal = {
								x: cb.y * ab.z - cb.z * ab.y,
								y: cb.z * ab.x - cb.x * ab.z,
								z: cb.x * ab.y - cb.y * ab.x
							};
							
							const length = Math.sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z);
							if (length > 0) {
								normal.x /= length;
								normal.y /= length;
								normal.z /= length;
							}
							
							dst.push(normal.x, normal.y, normal.z);
							dst.push(normal.x, normal.y, normal.z);
							dst.push(normal.x, normal.y, normal.z);
						}
					}
					
					// ============== 解析主流程 ==============
					setTimeout(() => {
						this.loadingProgress.update("Processing vertices and faces...", 98.5);
					}, 500);
					
					// 预处理文本
					if (objText.indexOf("\\r\\n") !== -1) {
						objText = objText.replace(/\\r\\n/g, "\\n");
					}
					
					const lines = objText.split("\\n");
					const state = new ParserState();
					
					// 解析每一行
					for (let i = 0, l = lines.length; i < l; i++) {
						const line = lines[i].trimStart();
						if (line.length === 0) continue;
						
						const lineFirstChar = line.charAt(0);
						
						if (lineFirstChar === "#") continue;
						
						if (lineFirstChar === "v") {
							const data = line.split(_face_vertex_data_separator_pattern);
							switch (data[0]) {
								case "v":
									state.vertices.push(
										parseFloat(data[1]),
										parseFloat(data[2]),
										parseFloat(data[3])
									);
									if (data.length >= 7) {
										// 处理顶点颜色（如果存在）
										const color = new THREE.Color();
										color.setRGB(parseFloat(data[4]), parseFloat(data[5]), parseFloat(data[6]));
										state.colors.push(color.r, color.g, color.b);
									}
									break;
								case "vn":
									state.normals.push(
										parseFloat(data[1]),
										parseFloat(data[2]),
										parseFloat(data[3])
									);
									break;
								case "vt":
									state.uvs.push(
										parseFloat(data[1]),
										parseFloat(data[2])
									);
									break;
							}
						} else if (lineFirstChar === "f") {
							const lineData = line.slice(1).trim();
							const vertexData = lineData.split(_face_vertex_data_separator_pattern);
							const faceVertices = [];
							
							// 解析面的顶点数据
							for (let j = 0, jl = vertexData.length; j < jl; j++) {
								const vertex = vertexData[j];
								if (vertex.length > 0) {
									const vertexParts = vertex.split("/");
									faceVertices.push(vertexParts);
								}
							}
							
							// 将多边形三角化（使用官方OBJLoader的三角化方法）
							if (faceVertices.length >= 3) {
								const v1 = faceVertices[0];
								for (let j = 1, jl = faceVertices.length - 1; j < jl; j++) {
									const v2 = faceVertices[j];
									const v3 = faceVertices[j + 1];
									
									state.addFace(
										v1[0] || "", v2[0] || "", v3[0] || "",
										v1[1] || "", v2[1] || "", v3[1] || "",
										v1[2] || "", v2[2] || "", v3[2] || ""
									);
								}
							}
						} else {
							let result = _object_pattern.exec(line);
							if (result !== null) {
								// o object_name 或 g group_name
								const name = (" " + result[0].slice(1).trim()).slice(1);
								state.startObject(name);
							} else if (_material_use_pattern.test(line)) {
								// usemtl
								state.object.startMaterial(line.substring(7).trim(), state.materialLibraries);
							} else if (_material_library_pattern.test(line)) {
								// mtllib
								state.materialLibraries.push(line.substring(7).trim());
							} else if (lineFirstChar === "s") {
								const result = line.split(" ");
								// 平滑组
								if (result.length > 1) {
									const value = result[1].trim().toLowerCase();
									state.object.smooth = (value !== "0" && value !== "off");
								} else {
									state.object.smooth = true;
								}
								const material = state.object.currentMaterial();
								if (material) material.smooth = state.object.smooth;
							}
						}
					}
					
					state.finalize();
					
					// ============== 创建Three.js对象 ==============
					const container = new THREE.Group();
					const hasPrimitives = !(state.objects.length === 1 && state.objects[0].geometry.vertices.length === 0);
					
					if (hasPrimitives) {
						for (let i = 0, l = state.objects.length; i < l; i++) {
							const object = state.objects[i];
							const geometry = object.geometry;
							const materials = object.materials;
							
							if (geometry.vertices.length === 0) continue;
							
							const buffergeometry = new THREE.BufferGeometry();
							buffergeometry.setAttribute(
								"position", 
								new THREE.Float32BufferAttribute(geometry.vertices, 3)
							);
							
							if (geometry.normals.length > 0) {
								buffergeometry.setAttribute(
									"normal", 
									new THREE.Float32BufferAttribute(geometry.normals, 3)
								);
							}
							
							if (geometry.uvs.length > 0) {
								buffergeometry.setAttribute(
									"uv", 
									new THREE.Float32BufferAttribute(geometry.uvs, 2)
								);
							}
							
							// 创建材质
							const createdMaterials = [];
							for (let mi = 0, miLen = materials.length; mi < miLen; mi++) {
								const sourceMaterial = materials[mi];
								
								let material;
								if (materialsDict && materialsDict[sourceMaterial.name]) {
									material = materialsDict[sourceMaterial.name];
								} else {
									material = this.createDefaultMaterial();
									material.name = sourceMaterial.name || "default";
								}
								
								createdMaterials.push(material);
							}
							
							// 创建网格
							let mesh;
							if (createdMaterials.length > 1) {
								// 为每个材质添加组
								for (let mi = 0, miLen = materials.length; mi < miLen; mi++) {
									const sourceMaterial = materials[mi];
									if (sourceMaterial.groupCount > 0) {
										buffergeometry.addGroup(sourceMaterial.groupStart, sourceMaterial.groupCount, mi);
									}
								}
								mesh = new THREE.Mesh(buffergeometry, createdMaterials);
							} else {
								mesh = new THREE.Mesh(buffergeometry, createdMaterials[0]);
							}
							
							mesh.name = object.name || "obj_mesh";
							
							// 根据当前阴影设置启用阴影
							mesh.castShadow = this.state.lights.shadowsEnabled;
							mesh.receiveShadow = this.state.lights.shadowsEnabled;
							
							container.add(mesh);
						}
					} else {
						// 如果只有点数据，创建点云
						if (state.vertices.length > 0) {
							const material = new THREE.PointsMaterial({ size: 0.1, color: 0xffffff });
							const geometry = new THREE.BufferGeometry();
							geometry.setAttribute("position", new THREE.Float32BufferAttribute(state.vertices, 3));
							const points = new THREE.Points(geometry, material);
							container.add(points);
						}
					}
					
					this.loadingProgress.update("Creating 3D objects...", 99.5);
					return container;
					
				} catch (error) {
					console.log("Parse OBJ manually failed: ", error);
					throw error;
				}
			}

			// load mtl zip
			async loadMTLFromZip(mtlText, mainFilePath, virtualFS, options = {}) {
				return new Promise((resolve, reject) => {
					try {
						// 创建统一的纹理加载器
						this.loadingProgress.update("Parsing MTL file...", 97.5);
						const textureLoader = new TextureLoaderFromZip(virtualFS);
						
						// 使用改进的解析器
						const parser = new MTLParser();
						const materialsInfo = parser.parseMTLText(mtlText);
						
						if (Object.keys(materialsInfo).length === 0) {
							resolve({});
							return;
						}
						
						// 合并选项
						const defaultOptions = {
							materialPreset: 'standard',
							normalizeRGB: false,
							ignoreZeroRGBs: false,
							invertTrProperty: false
						};
						
						const mergedOptions = { ...defaultOptions, ...options };
						
						// 创建材质字典
						const materialsDict = {};
						
						// 收集所有需要加载的纹理信息
						const textureInfos = [];
						const textureToMaterials = new Map();
						
						this.loadingProgress.update("Creating materials...", 98);
						
						for (const materialName in materialsInfo) {
							const materialInfo = materialsInfo[materialName];
							
							// 根据预设创建材质
							const threeMaterial = this.createMaterialFromMTLInfo(materialInfo);
							
							// 应用材质选项
							if (mergedOptions.normalizeRGB || mergedOptions.ignoreZeroRGBs || mergedOptions.invertTrProperty) {
								threeMaterial.userData = threeMaterial.userData || {};
								threeMaterial.userData.mtlOptions = {
									normalizeRGB: mergedOptions.normalizeRGB,
									ignoreZeroRGBs: mergedOptions.ignoreZeroRGBs,
									invertTrProperty: mergedOptions.invertTrProperty
								};
							}
							
							materialsDict[materialName] = threeMaterial;
							
							// 收集纹理信息
							const textures = parser.getTexturesForMaterial(materialInfo);
							for (const textureInfo of textures) {
								textureInfos.push({
									materialName: materialName,
									textureType: textureInfo.type,
									path: textureInfo.path,
									params: textureInfo.params
								});
								
								if (!textureToMaterials.has(textureInfo.path)) {
									textureToMaterials.set(textureInfo.path, []);
								}
								textureToMaterials.get(textureInfo.path).push({
									materialName: materialName,
									textureType: textureInfo.type,
									params: textureInfo.params
								});
							}
						}
						
						if (textureInfos.length === 0) {
							// 没有纹理，直接返回材质
							this.loadingProgress.update("Finalizing materials...", 98.5);
							this.finalizeMaterials(materialsDict, materialsInfo);
							textureLoader.dispose();
							resolve(materialsDict);
							return;
						}
						
						this.loadingProgress.update('Loading ' + textureInfos.length + ' textures...', 98.2);
						
						// 批量加载纹理
						textureLoader.loadTextures(
							textureInfos.map(info => ({ path: info.path })),
							mainFilePath
						).then(textureResults => {
							// 应用纹理到材质
							for (let i = 0; i < textureInfos.length; i++) {
								const info = textureInfos[i];
								const result = textureResults[i];
								
								if (result && result.texture) {
									const material = materialsDict[info.materialName];
									if (material) {
										this.applyTextureWithParams(material, result.texture, info, result.path);
									}
								}
							}
							
							// 最终材质调整
							this.loadingProgress.update("Finalizing materials...", 98.8);
							this.finalizeMaterials(materialsDict, materialsInfo);
							
							// 验证加载结果
							/* this.logMaterialTextureInfo(materialsDict); */
							
							// 清理纹理加载器
							textureLoader.dispose();
							
							resolve(materialsDict);
							
						}).catch(error => {
							// 即使纹理失败，也尝试最终调整
							this.finalizeMaterials(materialsDict, materialsInfo);
							
							// 清理纹理加载器
							textureLoader.dispose();
							
							resolve(materialsDict);
						});
						
					} catch (error) {
						console.log('Parse MTL failed:', error);
						reject(error);
					}
				});
			}

			finalizeMaterials(materialsDict, materialsInfo) {
				for (const materialName in materialsDict) {
					const material = materialsDict[materialName];
					const mtlInfo = materialsInfo[materialName];
					
					if (!mtlInfo) continue;
					
					// 确保透明度设置正确
					if (material.transparent && material.opacity === undefined) {
						material.opacity = 0.9;
					}
					
					// 确保双面材质正确设置
					if (material.side === undefined) {
						material.side = THREE.FrontSide;
					}
					
					// 更新材质
					material.needsUpdate = true;
					
					// 记录原始MTL信息
					material.userData = material.userData || {};
					material.userData.mtlInfo = {
						name: mtlInfo.name,
						hasTextures: !!(mtlInfo.map_Kd || mtlInfo.map_Ks || mtlInfo.map_Ke || 
									   mtlInfo.map_bump || mtlInfo.bump || mtlInfo.norm),
						originalIllum: mtlInfo.illum
					};
				}
			}

			createMaterialFromMTLInfo(mtlInfo, options = {}) {
				const defaults = {
					materialType: 'standard', // 'standard' 或 'phong'
					convertPhongToStandard: true,
					normalizeRGB: false,
					ignoreZeroRGBs: false,
					invertTrProperty: false
				};
				
				const settings = { ...defaults, ...options };
				
				// 如果指定使用Phong材质，则直接创建MeshPhongMaterial
				if (settings.materialType === 'phong') {
					return this.createPhongMaterialFromMTLInfo(mtlInfo, settings);
				}
				
				// 否则，使用智能转换创建MeshStandardMaterial
				return this.createStandardMaterialFromMTLInfo(mtlInfo, settings);
			}

			createPhongMaterialFromMTLInfo(mtlInfo, options = {}) {
				// 默认选项（与官方MTLLoader一致）
				const defaults = {
					side: THREE.FrontSide,
					wrap: THREE.RepeatWrapping,
					normalizeRGB: false,
					ignoreZeroRGBs: false,
					invertTrProperty: false
				};
				
				const settings = { ...defaults, ...options };
				
				// 创建材质参数对象（与官方MTLLoader完全一致）
				const params = {
					name: mtlInfo.name,
					side: settings.side
				};
				
				// =============== 处理颜色属性（与官方MTLLoader完全一致） ===============
				
				// 处理漫反射颜色 Kd
				if (mtlInfo.Kd) {
					let kdValue = mtlInfo.Kd;
					if (settings.normalizeRGB) {
						kdValue = kdValue.map(val => val / 255.0);
					}
					if (!settings.ignoreZeroRGBs || !(kdValue[0] === 0 && kdValue[1] === 0 && kdValue[2] === 0)) {
						params.color = new THREE.Color().fromArray(kdValue).convertSRGBToLinear();
					}
				}
				
				// 处理高光颜色 Ks
				if (mtlInfo.Ks) {
					let ksValue = mtlInfo.Ks;
					if (settings.normalizeRGB) {
						ksValue = ksValue.map(val => val / 255.0);
					}
					if (!settings.ignoreZeroRGBs || !(ksValue[0] === 0 && ksValue[1] === 0 && ksValue[2] === 0)) {
						params.specular = new THREE.Color().fromArray(ksValue).convertSRGBToLinear();
					}
				}
				
				// 处理自发光 Ke
				if (mtlInfo.Ke) {
					let keValue = mtlInfo.Ke;
					if (settings.normalizeRGB) {
						keValue = keValue.map(val => val / 255.0);
					}
					if (!settings.ignoreZeroRGBs || !(keValue[0] === 0 && keValue[1] === 0 && keValue[2] === 0)) {
						params.emissive = new THREE.Color().fromArray(keValue).convertSRGBToLinear();
					}
				}
				
				// =============== 处理标量属性（与官方MTLLoader完全一致） ===============
				
				// 处理高光指数 Ns
				if (mtlInfo.Ns !== undefined) {
					params.shininess = mtlInfo.Ns;
				}
				
				// =============== 透明度处理（与官方MTLLoader完全一致） ===============
				
				let opacity = 1.0;
				let transparent = false;
				
				// 处理 d（不透明度）
				if (mtlInfo.d !== undefined) {
					const dValue = mtlInfo.d;
					if (dValue < 1.0) {
						opacity = dValue;
						transparent = true;
					}
				}
				
				// 处理 Tr（透光度）
				if (mtlInfo.Tr !== undefined) {
					let trValue = mtlInfo.Tr;
					if (settings.invertTrProperty) {
						trValue = 1.0 - trValue;
					}
					if (trValue > 0) {
						opacity = 1.0 - trValue;
						transparent = true;
					}
				}
				
				// 如果有透明度贴图，也必须设置transparent
				if (mtlInfo.map_d) {
					transparent = true;
				}
				
				params.opacity = opacity;
				params.transparent = transparent;
				
				// =============== 创建材质 ===============
				
				const material = new THREE.MeshPhongMaterial(params);
				
				// 应用纹理包装设置
				if (settings.wrap !== undefined) {
					material.userData = material.userData || {};
					material.userData.wrap = settings.wrap;
				}
				
				// 记录原始MTL信息
				material.userData = material.userData || {};
				material.userData.mtlInfo = {
					name: mtlInfo.name,
					Kd: mtlInfo.Kd,
					Ks: mtlInfo.Ks,
					Ke: mtlInfo.Ke,
					Ns: mtlInfo.Ns,
					d: mtlInfo.d,
					Tr: mtlInfo.Tr,
					Ni: mtlInfo.Ni,
					illum: mtlInfo.illum
				};
				
				return material;
			}

			createStandardMaterialFromMTLInfo(mtlInfo, options = {}) {
				// 默认选项
				const defaults = {
					side: THREE.FrontSide,
					wrap: THREE.RepeatWrapping,
					normalizeRGB: false,
					ignoreZeroRGBs: false,
					invertTrProperty: false
				};
				
				const settings = { ...defaults, ...options };
				
				// 创建材质参数对象
				const params = {
					name: mtlInfo.name,
					side: settings.side
				};
				
				// =============== 处理颜色属性 ===============
				
				// 处理漫反射颜色 Kd
				if (mtlInfo.Kd) {
					let kdValue = mtlInfo.Kd;
					if (settings.normalizeRGB) {
						kdValue = kdValue.map(val => val / 255.0);
					}
					if (!settings.ignoreZeroRGBs || !(kdValue[0] === 0 && kdValue[1] === 0 && kdValue[2] === 0)) {
						params.color = new THREE.Color().fromArray(kdValue).convertSRGBToLinear();
					}
				}
				
				// 处理高光颜色 Ks
				if (mtlInfo.Ks) {
					let ksValue = mtlInfo.Ks;
					if (settings.normalizeRGB) {
						ksValue = ksValue.map(val => val / 255.0);
					}
					
					if (!settings.ignoreZeroRGBs || !(ksValue[0] === 0 && ksValue[1] === 0 && ksValue[2] === 0)) {
						const ksBrightness = (ksValue[0] + ksValue[1] + ksValue[2]) / 3;
						
						if (ksBrightness > 0.9) {
							params.metalness = 0.8;
							params.roughness = 0.1;
						} else if (ksBrightness > 0.3) {
							params.metalness = 0.0;
							params.roughness = 0.4;
						} else {
							params.metalness = 0.0;
							params.roughness = 0.8;
						}
					}
				}
				
				// 处理自发光 Ke
				if (mtlInfo.Ke) {
					let keValue = mtlInfo.Ke;
					if (settings.normalizeRGB) {
						keValue = keValue.map(val => val / 255.0);
					}
					
					if (!settings.ignoreZeroRGBs || !(keValue[0] === 0 && keValue[1] === 0 && keValue[2] === 0)) {
						params.emissive = new THREE.Color().fromArray(keValue).convertSRGBToLinear();
						const keBrightness = (keValue[0] + keValue[1] + keValue[2]) / 3;
						params.emissiveIntensity = keBrightness;
					}
				}
				
				// =============== 处理标量属性 ===============
				
				// 处理高光指数 Ns -> 粗糙度
				if (mtlInfo.Ns !== undefined) {
					const nsValue = mtlInfo.Ns;
					
					if (nsValue <= 0) {
						params.roughness = 1.0;
					} else if (nsValue >= 1000) {
						params.roughness = 0.04;
					} else {
						const normalizedNs = nsValue / 1000;
						params.roughness = 1.0 - Math.sqrt(normalizedNs);
						params.roughness = Math.max(0.04, Math.min(params.roughness, 1.0));
					}
				}
				
				// =============== 透明度处理（严格按照官方逻辑） ===============
				
				let opacity = 1.0;
				let transparent = false;
				
				// 处理 d（不透明度） - 严格按官方逻辑
				if (mtlInfo.d !== undefined) {
					const dValue = mtlInfo.d;
					if (dValue < 1.0) {
						opacity = dValue;
						transparent = true;
					} else {
						opacity = 1.0;
						transparent = false;
					}
				}
				
				// 处理 Tr（透光度） - 严格按官方逻辑，且只在有Tr属性时才处理
				if (mtlInfo.Tr !== undefined) {
					let trValue = mtlInfo.Tr;
					if (settings.invertTrProperty) {
						trValue = 1.0 - trValue;
					}
					if (trValue > 0) {
						opacity = 1.0 - trValue;
						transparent = true;
					}
				}
				
				// 如果有透明度贴图，必须设置透明
				if (mtlInfo.map_d) {
					transparent = true;
				}
				
				params.opacity = opacity;
				params.transparent = transparent;
				
				// =============== 其他属性处理 ===============
				
				// 折射率 Ni
				if (mtlInfo.Ni !== undefined && mtlInfo.Ni !== 1.0) {
					params.userData = params.userData || {};
					params.userData.ior = mtlInfo.Ni;
				}
				
				// 透射颜色 Tf
				
				// 光照模型 illum - 仅记录
				if (mtlInfo.illum !== undefined) {
					params.userData = params.userData || {};
					params.userData.illumModel = mtlInfo.illum;
				}
				
				// =============== 创建材质 ===============
				const material = new THREE.MeshStandardMaterial(params);
				
				// 记录原始MTL信息
				material.userData = material.userData || {};
				material.userData.mtlInfo = {
					name: mtlInfo.name,
					hasD: mtlInfo.d !== undefined,
					dValue: mtlInfo.d,
					hasTr: mtlInfo.Tr !== undefined,
					trValue: mtlInfo.Tr,
					hasMapD: mtlInfo.map_d !== null
				};
				
				return material;
			}

			applyTextureWithParams(material, texture, textureInfo, texturePath) {
				const params = textureInfo.params;
				
				// 更全面的纹理类型映射
				const propertyMap = {
					'map_Ka': 'aoMap',
					'map_Kd': 'map',
					'map_Ks': { 
						property: 'metalnessMap',
						conversion: function(texture) {
							texture.colorSpace = THREE.LinearSRGBColorSpace;
							return texture;
						}
					},
					'map_Ke': 'emissiveMap',
					'map_Ns': 'roughnessMap',
					'map_d': 'alphaMap',
					'map_bump': 'bumpMap',
					'bump': 'bumpMap',
					'norm': 'normalMap',
					'map_refl': 'envMap'
				};
				
				// FBX纹理类型映射
				const fbxPropertyMap = {
					'map': 'map',
					'normalMap': 'normalMap',
					'roughnessMap': 'roughnessMap',
					'metalnessMap': 'metalnessMap',
					'emissiveMap': 'emissiveMap',
					'alphaMap': 'alphaMap',
					'aoMap': 'aoMap',
					'bumpMap': 'bumpMap',
					'specularMap': 'specularMap'
				};
				
				let propertyName = textureInfo.textureType;
				let textureConverter = null;
				
				// 如果是MTL纹理类型，需要映射
				if (propertyMap[propertyName]) {
					const propInfo = propertyMap[propertyName];
					if (typeof propInfo === 'string') {
						propertyName = propInfo;
					} else if (propInfo && typeof propInfo === 'object') {
						propertyName = propInfo.property;
						textureConverter = propInfo.conversion;
					}
				}
				// 如果是FBX纹理类型，直接使用
				else if (!fbxPropertyMap[propertyName]) {
					return;
				}
				
				// 如果需要转换，应用转换
				let finalTexture = texture;
				if (textureConverter) {
					finalTexture = textureConverter(texture.clone());
				}
				
				// 设置纹理
				material[propertyName] = finalTexture;
				
				// 应用纹理参数（仅适用于MTL）
				if (params) {
					// 缩放
					if (params.scale && (params.scale.x !== 1 || params.scale.y !== 1)) {
						finalTexture.repeat.set(params.scale.x, params.scale.y);
					}
					
					// 偏移
					if (params.offset && (params.offset.x !== 0 || params.offset.y !== 0)) {
						finalTexture.offset.set(params.offset.x, params.offset.y);
					}
					
					// bump缩放
					if ((textureInfo.textureType === 'map_bump' || textureInfo.textureType === 'bump') && params.bumpScale !== 1) {
						material.bumpScale = params.bumpScale;
					}
					
					// 钳制
					if (params.clamp) {
						finalTexture.wrapS = THREE.ClampToEdgeWrapping;
						finalTexture.wrapT = THREE.ClampToEdgeWrapping;
					} else {
						finalTexture.wrapS = THREE.RepeatWrapping;
						finalTexture.wrapT = THREE.RepeatWrapping;
					}
					
					// 色彩空间处理
					switch(textureInfo.textureType) {
						case 'map_Kd':
						case 'map_Ke':
							finalTexture.colorSpace = THREE.SRGBColorSpace;
							break;
						case 'map_Ns':
						case 'map_bump':
						case 'bump':
						case 'norm':
							finalTexture.colorSpace = THREE.LinearSRGBColorSpace;
							break;
						default:
							finalTexture.colorSpace = THREE.LinearSRGBColorSpace;
					}
				}
				
				// 根据纹理类型设置材质属性
				switch(propertyName) {
					case 'aoMap':
						material.aoMapIntensity = 1.0;
						break;
					case 'bumpMap':
						material.bumpScale = params && params.bumpScale !== undefined ? params.bumpScale : 1;
						break;
					case 'normalMap':
						material.normalScale = new THREE.Vector2(1, 1);
						break;
					case 'roughnessMap':
						material.roughness = material.roughness || 1.0;
						break;
					case 'metalnessMap':
						material.metalness = material.metalness || 1.0;
						break;
				}
				
				material.needsUpdate = true;
			}

			logMaterialTextureInfo(materialsDict) {
				console.log('=== Material Detail ===');
				for (const materialName in materialsDict) {
					const material = materialsDict[materialName];
					console.log('Material: ' + materialName);
					console.log('  Type: ' + material.type);
					
					if (material.color) {
						console.log('  Base Color: (' + 
							material.color.r.toFixed(2) + ', ' +
							material.color.g.toFixed(2) + ', ' +
							material.color.b.toFixed(2) + ')');
					}
					
					if (material.emissive) {
						const e = material.emissive;
						console.log('  Emissive Color: (' + 
							e.r.toFixed(2) + ', ' + e.g.toFixed(2) + ', ' + e.b.toFixed(2) + 
							') Intensity: ' + (material.emissiveIntensity || 0).toFixed(2));
					}
					
					if (material.metalness !== undefined) {
						console.log('  Metalness: ' + material.metalness.toFixed(2));
					}
					
					if (material.roughness !== undefined) {
						console.log('  Roughness: ' + material.roughness.toFixed(2));
					}
					
					if (material.opacity !== undefined && material.opacity < 1.0) {
						console.log('  Opacity: ' + material.opacity.toFixed(2));
					}
					
					const textureProps = ['map', 'aoMap', 'specularMap', 'emissiveMap', 
										 'roughnessMap', 'metalnessMap', 'alphaMap', 
										 'bumpMap', 'normalMap'];
					
					let hasTextures = false;
					for (const prop of textureProps) {
						if (material[prop]) {
							console.log('  - ' + prop + ': yes');
							hasTextures = true;
						}
					}
					
					if (!hasTextures) {
						console.log('  - Textures: no');
					}
				}
				console.log('===================');
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
				this.materialConversionCache.clear();
				this.disposeMaterialCache();
				this.scene.traverse(object => {
					if (object.isMesh && object.material) {
						this.textureManager.disposeMaterialTextures(object.material);
					}
				});
				
				// 重置纹理相关状态
				this.state.useVertexColors = false;
				this.state.textureMapping = true;
				
				// 6. 重置包围盒缓存
				this.state.sceneBBox = null;
				this.state.sceneCenter = new THREE.Vector3();
				
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
				
				// 7. 重置核心状态
				this.state.cameras.currentType = 'default';
				this.state.cameras.activeScene = null;
				this.state.cameraAnim.keyframes = [];
				this.state.cameraAnim.isEnabled = false;
				this.state.autoAddKeyframeEnabled = false;
				this.hideMaterialGUI();
				this.clearSelection();
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
				this.state.playback.totalFrames = 0;
				
				// 清理场景内容（包括场景相机及其状态）
				await this.cleanupPreviousModel();
				
				this.resetSettings();
				
				// 重置场景数据
				this.state.currentFormat = null;
				this.state.currentFileData = null;
				
				this.updateInfoDisplay();
				this.update3DDataButtonState();
				this.enableControls();
				this.renderInvalidate();
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
				
				// ============== 动画包围盒数据导出 ==============
				if (this.state.animationBBoxData.isInitialized) {
					const serializedBBoxData = this.serializeAnimationBBoxData();
					exportScene.userData.animationBBoxData = serializedBBoxData;
				}
				
				// ============== 场景信息 ==============
				exportScene.userData.sceneInfo = {
					format: this.state.currentFormat,
					hasAnimation: this.state.playback.totalFrames > 1,
					totalFrames: this.state.playback.totalFrames,
					fps: this.state.playback.fps,
					originalModelName: this.state.currentFileData?.filename || 'unknown'
				};
				
				// 设置导出选项
				const options = { 
					binary: true, 
					trs: false,
					onlyVisible: false,
					truncateDrawRange: false,
					animations: allAnimations,
					includeCustomExtensions: true,
					includeUserData: true,
					embedImages: true,
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
				
				// 创建一个共享的材质
				const sharedMaterial = this.createDefaultMaterial();
				
				// 确保材质和纹理可以被导出器正确处理
				if (sharedMaterial.map) {
					sharedMaterial.map.needsUpdate = true;
				}
				
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
					
					// 使用共享的材质
					const material = sharedMaterial;
					
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

			// 动画播放系统
			performRendering() {
				const mode = this.state.materialMode;
				
				// 判断是否需要使用composer
				const useComposer = mode === 'contour' || mode === 'ssao' || mode === 'gtao';
				
				// 直接渲染模式
				if (!useComposer) {
					this.renderer.render(this.scene, this.camera);
					return;
				}
				
				// Contour 特殊处理
				if (mode === 'contour' && this.needsRender) {
					this.renderNormalTexture();
				}
				
				if (!this.composer) {
					this.renderer.render(this.scene, this.camera);
				} else {
					this.composer.render();
				}
			}

			renderOnce() {
			  this.performRendering();
			  this.needsRender = false;
			}

			renderStartLoop() {
				if (this.isLoopRunning) return;
				this.isLoopRunning = true;
				
				const frameInterval = 1000 / this.state.playback.maxFPS;
				let lastTime = 0;
				
				const loop = (time) => {
					if (!this.isLoopRunning) return;
					
					if (time - lastTime < frameInterval) {
						this._rafId = requestAnimationFrame(loop);
						return;
					}
					lastTime = time;
					
					const pb = this.state.playback;
					const delta = pb.clock.getDelta();
					
					if (pb.isPlaying && delta > 0) {
						const step = delta * pb.fps * (pb.isReversed ? -1 : 1);
						let newFrame = pb.currentFrame + step;
						
						// 录制模式下不要循环播放
						if (this.state.recording.isRecording) {
							if (newFrame > pb.endFrame) {
								newFrame = pb.endFrame;
								pb.isPlaying = false;
								this.dom.btns.play.textContent = "▶️";
								this.dom.btns.reverse.textContent = "◀️";
							} else if (newFrame < pb.startFrame) {
								newFrame = pb.startFrame;
							}
						} else {
							// 非录制时正常循环
							if (newFrame > pb.endFrame) newFrame = pb.startFrame;
							if (newFrame < pb.startFrame) newFrame = pb.endFrame;
						}
						
						pb.currentFrame = newFrame;
						
						this.seek(pb.currentFrame);
						this.needsRender = true;
					}
					
					if (this.needsRender) this.renderOnce();
					
					this._rafId = requestAnimationFrame(loop);
				};
				
				this._rafId = requestAnimationFrame(loop);
			}

			renderStopLoop() {
				this.isLoopRunning = false;
				
				if (this._rafId) {
					cancelAnimationFrame(this._rafId);
					this._rafId = null;
				}
				
				this.state.playback.clock.stop();
			}

			renderInvalidate() {
				this.needsRender = true;
				this.renderOnce();
			}

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
				
				/* this.updateFPSInfo(frame); */
				
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
				this.renderStartLoop();
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

			pause() {
				this.state.playback.isPlaying = false;
				this.dom.btns.play.textContent = "▶️";
				this.dom.btns.reverse.textContent = "◀️";
				
				this.renderStopLoop();
				this.renderInvalidate();
			}

			seek(frame) {
				const pb = this.state.playback;
				pb.currentFrame = Math.max(pb.startFrame, Math.min(frame, pb.endFrame));
				this.updateTimeSleder();
				
				this.updateVisuals(Math.floor(pb.currentFrame));
				
				if (!pb.isPlaying) this.renderInvalidate();
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
					this.renderInvalidate();
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

			// 录像系统
			captureScreenshot(customFilename = null) {
				/* const originalGridVisible = this.dom.toggles.helper.checked;
				const originalInfoVisible = this.dom.toggles.info.checked; */
				
				try {
					/* this.dom.toggles.helper.checked = false;
					this.dom.toggles.info.checked = false;
					this.toggleHelper();
					this.toggleInfoDisplay(); */
					
					// 确保渲染了当前帧
					this.renderInvalidate();
					
					// 从渲染器的canvas获取数据URL
					const canvas = this.renderer.domElement;
					const dataURL = canvas.toDataURL('image/png');
					
					// 如果有自定义文件名，直接返回blob，不下载
					if (customFilename) {
						// 将dataURL转换为blob
						const blob = this.dataURLToBlob(dataURL);
						return {
							blob: blob,
							filename: customFilename,
							dataURL: dataURL
						};
					} else {
						// 原逻辑：创建下载链接
						const link = document.createElement('a');
						const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
						
						// 获取模型名称（如果有的话）
						let modelName = 'screenshot';
						if (this.state.currentFileData && this.state.currentFileData.filename) {
							const fileName = this.state.currentFileData.filename.split('/').pop().split('.')[0];
							modelName = fileName;
						}
						
						// 添加当前帧信息
						const frameInfo = this.state.playback.totalFrames > 1 
							? "_frame" + Math.floor(this.state.playback.currentFrame).toString().padStart(4, '0') 
							: '';
							
						const filename = modelName + frameInfo + "_" + timestamp + ".png";
						
						link.href = dataURL;
						link.download = filename;
						link.style.display = 'none';
						
						// 添加到页面并触发点击
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
						
						// 显示成功消息
						this.showMessage("Screenshot saved: " + filename, 3000);
					}
					
				} catch (error) {
					this.showMessage('Sceenshot Failed: ' + error.message, 5000);
					return null;
				} finally {
					/* this.dom.toggles.helper.checked = originalGridVisible;
					this.dom.toggles.info.checked = originalInfoVisible;
					this.toggleHelper();
					this.toggleInfoDisplay(); */
				}
			}

			dataURLToBlob(dataURL) {
				const arr = dataURL.split(',');
				const mime = arr[0].match(/:(.*?);/)[1];
				const bstr = atob(arr[1]);
				let n = bstr.length;
				const u8arr = new Uint8Array(n);
				
				while (n--) {
					u8arr[n] = bstr.charCodeAt(n);
				}
				
				return new Blob([u8arr], { type: mime });
			}

			async startRecording() {
				if (this.state.recording.isRecording) return;
				
				/* this.state.recording.originalGridVisible = this.dom.toggles.helper.checked;
				this.state.recording.originalInfoVisible = this.dom.toggles.info.checked;
				this.dom.toggles.helper.checked = false;
				this.dom.toggles.info.checked = false;
				this.toggleHelper();
				this.toggleInfoDisplay(); */
				
				this.disableControls();
				await new Promise(resolve => setTimeout(resolve, 50));
				
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
						
						/* this.dom.toggles.helper.checked = this.state.recording.originalGridVisible;
						this.dom.toggles.info.checked = this.state.recording.originalInfoVisible;
						this.toggleHelper();
						this.toggleInfoDisplay(); */
						
						this.enableControls();
						
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
					
					// 添加定期检查器，在录制状态下检查是否到达最后一帧
					const checkRecordingEnd = () => {
						if (!this.state.recording.isRecording) return;
						
						const pb = this.state.playback;
						const isAtEnd = Math.floor(pb.currentFrame) >= pb.endFrame;
						
						if (isAtEnd && this.state.recording.mediaRecorder && 
							this.state.recording.mediaRecorder.state === 'recording') {
							
							// 停止录制
							this.state.recording.mediaRecorder.stop();
							this.pause();
						} else if (this.state.recording.isRecording) {
							// 继续检查
							setTimeout(checkRecordingEnd, 50); // 每50ms检查一次
						}
					};
					
					// 开始检查
					setTimeout(checkRecordingEnd, 100);
				} catch (e) { 
					this.showMessage("Recording setup failed: " + e.message, 5000); 
				}
			}

			async getScene3DData() {
				// 0. 检查场景是否为空或有选中物体
				let targetName = '';
				let useSelectedObject = false;
				
				// 如果有选中物体，优先使用选中物体
				if (this.state.selection.isSelecting && this.state.selection.selectedObject) {
					const selectedObject = this.state.selection.selectedObject;
					targetName = selectedObject.name || 'Selected Object';
					useSelectedObject = true;
					
					// 验证选中物体是否有有效包围盒
					const bbox = new THREE.Box3().setFromObject(selectedObject);
					if (bbox.isEmpty()) {
						this.showMessage('Selected object has empty bounding box.', 3000);
						useSelectedObject = false;
					}
				}
				
				// 如果没有选中物体或选中物体无效，使用整个场景
				if (!useSelectedObject) {
					const bboxData = this.getBBoxForCurrentFrame();
					if (bboxData.isEmpty) {
						this.showMessage('Scene is empty. Cannot generate 3D data.', 3000);
						return;
					}
					targetName = 'Scene';
				}
				
				// 禁用控制面板
				this.disableControls();
				
				// 显示加载状态
				this.dom.loading.style.display = 'block';
				this.dom.loadingText.textContent = useSelectedObject ? 
					'Generating 3D data for selected object ' + targetName + '...' : 
					'Generating 3D data for entire scene...';
				this.dom.loadingProgressBar.style.width = '0%';
				this.dom.loadingPercentage.textContent = '0%';
				this.dom.loadingPercentage.style.display = 'block';
				
				// 保存选择辅助线原始可见性
				let originalSelectionBBoxVisible = true;
				let originalSelectionHelperVisible = true;
				
				if (this.state.selection.isSelecting) {
					if (this.state.selection.selectionBBox) {
						originalSelectionBBoxVisible = this.state.selection.selectionBBox.visible;
						this.state.selection.selectionBBox.visible = false;
					}
					if (this.state.selection.selectionHelper) {
						originalSelectionHelperVisible = this.state.selection.selectionHelper.visible;
						this.state.selection.selectionHelper.visible = false;
					}
				}
				
				// 保存当前背景颜色
				const originalBackground = this.scene.background ? this.scene.background.clone() : new THREE.Color(0x111111);
				
				try {
					// 获取场景名称（如果有选中物体，添加到名称中）
					let sceneName = 'scene';
					if (this.state.currentFileData && this.state.currentFileData.filename) {
						const fileName = this.state.currentFileData.filename.split('/').pop().split('.')[0];
						sceneName = fileName;
						
						if (useSelectedObject) {
							// 在场景名称中添加选中物体信息
							const objName = this.state.selection.selectedObject.name || 'selected';
							sceneName = fileName + '_' + objName.replace(/[^a-zA-Z0-9_-]/g, '_');
						}
					}
					
					// 1. 获取所有默认正交相机
					const orthographicCameras = this.state.cameras.default.filter(camera => 
						camera.isOrthographicCamera
					);
					
					if (orthographicCameras.length === 0) {
						this.showMessage('No orthographic cameras found.', 3000);
						return;
					}
					
					// 定义相机顺序映射
					const cameraOrder = {
						'Front': 1,
						'Left': 2,
						'Back': 3,
						'Right': 4,
						'Top': 5,
						'Bottom': 6
					};
					
					// 保存当前相机状态
					const originalCamera = this.camera;
					const originalControlsTarget = this.controls.target.clone();
					const originalControlsEnabled = this.controls.enabled;
					const originalCameraType = this.state.cameras.currentType;
					const originalMaterialMode = this.state.materialMode;
					const originalFOV = this.camera.fov;
					const originalNear = this.camera.near;
					const originalFar = this.camera.far;
					
					// 保存当前光照强度
					const originalDirLightIntensity = this.state.lights.dirIntensity || this.state.lights.dir.intensity;
					const originalAmbLightIntensity = this.state.lights.ambIntensity || this.state.lights.amb.intensity;
					const originalUseSceneLight = this.state.useSceneLight;
					
					// 确保使用默认灯光模式
					this.state.useSceneLight = false;
					if (this.dom.toggles.light) {
						this.dom.toggles.light.checked = false;
					}
					
					// 显示默认灯光
					if (this.state.lights.dir) {
						this.state.lights.dir.visible = true;
					}
					if (this.state.lights.amb) {
						this.state.lights.amb.visible = true;
					}
					
					// 设置默认光源强度
					this.state.lights.dirIntensity = 0;
					this.state.lights.ambIntensity = 10;
					
					if (this.state.lights.dir) {
						this.state.lights.dir.intensity = 0;
					}
					if (this.state.lights.amb) {
						this.state.lights.amb.intensity = 10;
					}
					
					// 存储截图的数组
					const screenshots = [];
					
					// 定义材质列表
					const materials = ['Original', 'Normal', 'Depth', 'Edge'];
					const suffixes = ['O', 'N', 'D', 'E'];
					
					// 每个相机8步（切换+重置+居中+聚焦+5种材质截图）
					const stepsPerCamera = 8;
					const totalSteps = orthographicCameras.length * stepsPerCamera;
					let currentStep = 0;
					
					// 遍历每个正交相机
					for (let i = 0; i < orthographicCameras.length; i++) {
						const camera = orthographicCameras[i];
						const cameraName = camera.name || 'ortho_camera_' + i;
						const cameraOrderId = cameraOrder[cameraName] || i + 1;
						
						// 更新进度
						currentStep++;
						const progress = Math.round((currentStep / totalSteps) * 100);
						this.dom.loadingProgressBar.style.width = progress + '%';
						this.dom.loadingPercentage.textContent = progress + '%';
						this.dom.loadingText.textContent = useSelectedObject ? 
							'Setting up ' + cameraName + ' for selected object...' : 
							'Setting up ' + cameraName + '...';
						
						// a. 切换到该相机
						this.camera = camera;
						this.controls.object = camera;
						this.controls.enabled = true;
						this.state.cameras.currentType = 'default';
						
						// 更新相机UI
						this.updateCameraUIForMode();
						await this.waitForNextFrame();
						
						// b. 重置相机到默认状态
						currentStep++;
						const progressReset = Math.round((currentStep / totalSteps) * 100);
						this.dom.loadingProgressBar.style.width = progressReset + '%';
						this.dom.loadingPercentage.textContent = progressReset + '%';
						this.dom.loadingText.textContent = useSelectedObject ? 
							'Resetting ' + cameraName + ' for selected object...' : 
							'Resetting ' + cameraName + '...';
						
						this.resetCamera();
						await this.waitForNextFrame();
						
						// c. 执行centerToObject
						currentStep++;
						const progressCenter = Math.round((currentStep / totalSteps) * 100);
						this.dom.loadingProgressBar.style.width = progressCenter + '%';
						this.dom.loadingPercentage.textContent = progressCenter + '%';
						this.dom.loadingText.textContent = useSelectedObject ? 
							'Centering ' + cameraName + ' to selected object...' : 
							'Centering ' + cameraName + ' to object...';
						
						this.centerToObject();
						await this.waitForNextFrame();
						
						// d. 执行focusToObject
						currentStep++;
						const progressFocus = Math.round((currentStep / totalSteps) * 100);
						this.dom.loadingProgressBar.style.width = progressFocus + '%';
						this.dom.loadingPercentage.textContent = progressFocus + '%';
						this.dom.loadingText.textContent = useSelectedObject ? 
							'Focusing ' + cameraName + ' to selected object...' : 
							'Focusing ' + cameraName + ' to object...';
						
						this.focusToObject();
						await this.waitForNextFrame();
						
						// e. 依次切换到Original, Normal, Depth, Edge, GTAO材质并截屏
						for (let j = 0; j < materials.length; j++) {
							currentStep++;
							const progress3 = Math.round((currentStep / totalSteps) * 100);
							this.dom.loadingProgressBar.style.width = progress3 + '%';
							this.dom.loadingPercentage.textContent = progress3 + '%';
							this.dom.loadingText.textContent = useSelectedObject ? 
								'Capturing ' + materials[j] + ' for selected object (' + cameraName + ')...' : 
								'Capturing ' + materials[j] + ' for ' + cameraName + '...';
							
							// 切换到材质
							const materialMode = materials[j].toLowerCase();
							this.handleMatChange(materialMode);
							await this.waitForNextFrame();
							
							// 对于original材质，设置背景为纯黑色
							if (materialMode === 'original') {
								this.scene.background = new THREE.Color(0x000000);
							}
							
							// 截屏文件名格式: {scenename}_{ID}_{camera}_{suffix}.png
							// 如果有选中物体，在文件名中标记
							let filename;
							if (useSelectedObject) {
								const objName = this.state.selection.selectedObject.name || 'selected';
								const safeObjName = objName.replace(/[^a-zA-Z0-9_-]/g, '_');
								filename = sceneName + '_' + cameraOrderId + '_' + cameraName + '_' + suffixes[j] + '_' + safeObjName + '.png';
							} else {
								filename = sceneName + '_' + cameraOrderId + '_' + cameraName + '_' + suffixes[j] + '.png';
							}
							const screenshot = this.captureScreenshot(filename);
							
							if (screenshot) {
								screenshots.push({
									blob: screenshot.blob,
									filename: filename,
									camera: cameraName,
									cameraId: cameraOrderId,
									material: materials[j],
									materialFolder: materials[j].toLowerCase(),
									object: useSelectedObject ? targetName : null
								});
							}
							
							await this.waitForNextFrame();
						}
						
						// 恢复原始材质
						this.handleMatChange(originalMaterialMode);
						await this.waitForNextFrame();
					}
					
					// 恢复原始相机状态
					this.camera = originalCamera;
					this.controls.object = originalCamera;
					this.controls.target.copy(originalControlsTarget);
					this.controls.enabled = originalControlsEnabled;
					this.state.cameras.currentType = originalCameraType;
					
					// 恢复相机参数
					this.camera.fov = originalFOV;
					this.camera.near = originalNear;
					this.camera.far = originalFar;
					this.camera.updateProjectionMatrix();
					
					this.updateCameraUIForMode();
					await this.waitForNextFrame();
					
					// 恢复原始光照强度
					this.state.lights.dirIntensity = originalDirLightIntensity;
					this.state.lights.ambIntensity = originalAmbLightIntensity;
					this.state.useSceneLight = originalUseSceneLight;
					
					if (this.state.lights.dir) {
						this.state.lights.dir.intensity = originalDirLightIntensity;
					}
					if (this.state.lights.amb) {
						this.state.lights.amb.intensity = originalAmbLightIntensity;
					}
					
					// 恢复灯光模式UI
					if (this.dom.toggles.light) {
						this.dom.toggles.light.checked = originalUseSceneLight;
					}
					
					// 更新灯光可视化
					this.updateVisualizationVisibility();
					
					// 恢复原始背景颜色
					this.scene.background = originalBackground;
					
					// 4. 将所有截屏打包输出并下载
					if (screenshots.length > 0) {
						this.showMessage("Starting to package screenshots...", 10000);
						await this.waitForNextFrame();
						await this.packageAndDownloadScreenshots(screenshots, sceneName);
					} else {
						this.showMessage("No screenshots were captured.", 3000);
					}
					
				} catch (error) {
					console.log("Error in getScene3DData:", error);
					this.showMessage("Error generating 3D data: " + error.message, 5000);
					
					// 即使出错，也尝试恢复原始光照强度
					try {
						const originalDirLightIntensity = this.state.getScene3DData?.originalDirLightIntensity;
						const originalAmbLightIntensity = this.state.getScene3DData?.originalAmbLightIntensity;
						const originalUseSceneLight = this.state.getScene3DData?.originalUseSceneLight;
						if (originalDirLightIntensity !== undefined && this.state.lights.dir) {
							this.state.lights.dir.intensity = originalDirLightIntensity;
							this.state.lights.dirIntensity = originalDirLightIntensity;
						}
						if (originalAmbLightIntensity !== undefined && this.state.lights.amb) {
							this.state.lights.amb.intensity = originalAmbLightIntensity;
							this.state.lights.ambIntensity = originalAmbLightIntensity;
						}
						if (originalUseSceneLight !== undefined) {
							this.state.useSceneLight = originalUseSceneLight;
						}
						if (this.dom.toggles.light) {
							this.dom.toggles.light.checked = originalUseSceneLight;
						}
						if (originalBackground !== undefined) {
							this.scene.background = originalBackground;
						}
						this.updateVisualizationVisibility();
					} catch (recoveryError) {
						console.error("Error recovering light settings:", recoveryError);
					}
					
				} finally {
					// 恢复选择辅助线可见性
					if (this.state.selection.isSelecting) {
						if (this.state.selection.selectionBBox) {
							this.state.selection.selectionBBox.visible = originalSelectionBBoxVisible;
						}
						if (this.state.selection.selectionHelper) {
							this.state.selection.selectionHelper.visible = originalSelectionHelperVisible;
						}
					}
					
					// 恢复控制面板
					this.enableControls();
					
					// 隐藏加载状态
					this.dom.loading.style.display = 'none';
					this.dom.loadingPercentage.style.display = 'none';
					
					// 更新界面
					this.renderInvalidate();
				}
			}

			waitForNextFrame() {
				return new Promise(resolve => {
					requestAnimationFrame(() => {
						setTimeout(resolve, 100);
					});
				});
			}

			async packageAndDownloadScreenshots(screenshots, sceneName) {
				try {
					// 创建zip文件
					const zip = new this.JSZip();
					
					// 按材质创建子目录
					const materialFolders = {};
					
					// 遍历所有截图，按材质分类
					screenshots.forEach((screenshot, index) => {
						const materialFolder = screenshot.materialFolder || screenshot.material.toLowerCase();
						
						// 创建材质子目录（如果尚未创建）
						if (!materialFolders[materialFolder]) {
							materialFolders[materialFolder] = zip.folder(materialFolder);
						}
						
						// 将截图添加到对应的材质子目录
						materialFolders[materialFolder].file(screenshot.filename, screenshot.blob);
					});
					
					// 生成zip文件
					const zipBlob = await zip.generateAsync({ type: "blob" });
					
					// 创建下载链接
					const zipFilename = sceneName + '_3d_data_' + Date.now() + '.zip';
					const url = URL.createObjectURL(zipBlob);
					const a = document.createElement('a');
					a.href = url;
					a.download = zipFilename;
					a.style.display = 'none';
					
					// 添加到页面并触发点击
					document.body.appendChild(a);
					a.click();
					
					// 清理
					setTimeout(() => {
						document.body.removeChild(a);
						URL.revokeObjectURL(url);
					}, 100);
					
					// 显示成功消息
					this.showMessage('3D data package (' + screenshots.length + ' screenshots in ' + Object.keys(materialFolders).length + ' folders) downloaded: ' + zipFilename, 5000);
					
				} catch (error) {
					console.log("Error packaging screenshots:", error);
					this.showMessage("Error creating package: " + error.message, 5000);
					
					// 如果打包失败，尝试单独下载每个文件
					this.downloadScreenshotsIndividually(screenshots);
				}
			}

			downloadScreenshotsIndividually(screenshots) {
				screenshots.forEach((screenshot, index) => {
					setTimeout(() => {
						const url = URL.createObjectURL(screenshot.blob);
						const a = document.createElement('a');
						a.href = url;
						a.download = screenshot.filename;
						a.style.display = 'none';
						
						document.body.appendChild(a);
						a.click();
						
						setTimeout(() => {
							document.body.removeChild(a);
							URL.revokeObjectURL(url);
						}, 100);
					}, index * 100);
				});
				
				this.showMessage('Downloading ' + screenshots.length + ' screenshots individually...', 5000);
			}

			update3DDataButtonState() {
				const bboxData = this.getBBoxForCurrentFrame();
				const hasMesh = !bboxData.isEmpty;
				const hasSelection = this.state.selection.isSelecting;
				
				if (this.dom.btns.threedDataBtn) {
					this.dom.btns.threedDataBtn.disabled = !hasMesh;
					
					if (!hasMesh) {
						this.dom.btns.threedDataBtn.title = "No mesh in scene";
					} else if (hasSelection) {
						this.dom.btns.threedDataBtn.title = "Get 3D data for selected object";
					} else {
						this.dom.btns.threedDataBtn.title = "Get Scene 3D Data";
					}
					
					if (hasMesh) {
						this.dom.btns.threedDataBtn.classList.remove('disabled-control');
					} else {
						this.dom.btns.threedDataBtn.classList.add('disabled-control');
					}
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
						emissive: new THREE.Color(params.emissive),
						emissiveIntensity: params.emissiveIntensity,
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

			updateDefaultMaterial() {
				const material = this.state.materials.default;
				const params = this.state.materialParams.default;
				
				if (material) {
					material.color.set(params.color);
					material.roughness = params.roughness;
					material.metalness = params.metalness;
					material.emissive.set(params.emissive),
					material.emissiveIntensity = params.emissiveIntensity;
					material.side = this.getSideValue(this.state.commonParams.side);
					material.flatShading = params.flatShading;
					material.needsUpdate = true;
				}
				
				this.renderInvalidate();
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
				
				this.renderInvalidate();
			}

			updateNormalMaterial() {
				const material = this.state.materials.normal;
				const params = this.state.materialParams.normal;
				
				if (material) {
					material.flatShading = params.flatShading;
					material.needsUpdate = true;
				}
				
				this.renderInvalidate();
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
				
				this.renderInvalidate();
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
				
				this.renderInvalidate();
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
				
				this.renderInvalidate();
			}

			resetDefaultParameters() {
				const defaultMaterialParams = {
					color: '#4a9eff',
					roughness: 1.0,
					metalness: 0.0,
					emissive: '#000000',
					emissiveIntensity: 0.0,
					flatShading: false
				};
				
				Object.assign(this.state.materialParams.default, defaultMaterialParams);
				this.updateDefaultMaterial();
				
				const controllers = this.state.materialGUI.defaultControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
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
				
				const controllers = this.state.materialGUI.wireframeControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
				}
			}

			resetNormalParameters() {
				const defaultNormalParams = {
					flatShading: false
				};
				
				Object.assign(this.state.materialParams.normal, defaultNormalParams);
				this.updateNormalMaterial();
				
				const controllers = this.state.materialGUI.normalControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
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
				
				const controllers = this.state.materialGUI.lineartControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
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
				
				const controllers = this.state.materialGUI.cannyControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
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
				
				const controllers = this.state.materialGUI.edgeControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
				}
			}

			// 后处理系统
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

			ensurePostProcessing() {
				if (this.composer) return;
				
				this.composer = new EffectComposer(this.renderer);
				
				const renderPass = new RenderPass(this.scene, this.camera);
				this.composer.addPass(renderPass);
				
				this._renderPass = renderPass;
			}

			disablePostProcessing() {
				if (!this.composer) return;
				
				// 只禁用非RenderPass的通道
				this.composer.passes.forEach(pass => {
					if (!(pass instanceof RenderPass)) {
						pass.enabled = false;
						pass.renderToScreen = false;
					} else {
						// 确保RenderPass启用并渲染到屏幕
						pass.enabled = true;
						pass.renderToScreen = true;
					}
				});
			}

			disableAllPostPasses() {
				if (!this.composer) return;
				this.composer.passes.forEach(p => p.enabled = false);
			}

			resizePostProcessing() {
				if (!this.composer) return;
				
				const size = this.renderer.getSize(new THREE.Vector2());
				this.composer.setSize(size.x, size.y);
				
				this.ssaoPass?.setSize?.(size.x, size.y);
				this.gtaoPass?.setSize?.(size.x, size.y);
				
				if (this.contourPass) {
					this.contourPass.uniforms.resolution.value.set(size.x, size.y);
				}
			}

			reorderPass(pass) {
				const passes = this.composer.passes;
				const i = passes.indexOf(pass);
				if (i !== -1 && i !== passes.length - 1) {
					passes.splice(i, 1);
					passes.push(pass);
				}
			}

			enableContour() {
				this.ensurePostProcessing();
				
				// 1. Pass
				if (!this.contourPass) this.createContourPass();
				
				// 2. Normal RT
				this.renderNormalTexture();
				
				// 3. 禁用其他 Pass
				this.disableAllPostPasses();
				
				// 4. 启用
				this.contourPass.enabled = true;
				this.contourPass.renderToScreen = true;
				
				// 确保RenderPass启用但不渲染到屏幕
				const renderPass = this.composer.passes.find(pass => pass instanceof RenderPass);
				if (renderPass) {
					renderPass.enabled = true;
					renderPass.renderToScreen = false;
				}
				
				// 5. 静态 uniform 绑定（一次）
				this.contourPass.uniforms.tNormal.value =
					this.normalRenderTarget.texture;
				
				if (this.depthTexture) {
					this.contourPass.uniforms.tDepth.value = this.depthTexture;
				}
				
				this.resizePostProcessing();
				this.renderInvalidate();
			}

			enableSSAO() {
				this.ensurePostProcessing();
				
				// 1. Pass
				if (!this.ssaoPass) this.createSSAOPass();
				
				// 2. 禁用其他 Pass
				this.disableAllPostPasses();
				
				// 3. 启用
				this.ssaoPass.enabled = true;
				this.ssaoPass.renderToScreen = true;
				
				// 确保RenderPass启用但不渲染到屏幕
				const renderPass = this.composer.passes.find(pass => pass instanceof RenderPass);
				if (renderPass) {
					renderPass.enabled = true;
					renderPass.renderToScreen = false;
				}
				
				this.reorderPass(this.ssaoPass);
				this.resizePostProcessing();
				this.renderInvalidate();
			}

			enableGTAO() {
				this.ensurePostProcessing();
				
				// 1. Pass
				if (!this.gtaoPass) this.createGTAOPass();
				
				// 2. 禁用其他 Pass
				this.disableAllPostPasses();
				
				// 3. 启用
				this.gtaoPass.enabled = true;
				this.gtaoPass.renderToScreen = true;
				
				// 确保RenderPass启用但不渲染到屏幕
				const renderPass = this.composer.passes.find(pass => pass instanceof RenderPass);
				if (renderPass) {
					renderPass.enabled = true;
					renderPass.renderToScreen = false;
				}
				
				this.reorderPass(this.gtaoPass);
				this.resizePostProcessing();
				this.renderInvalidate();
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
				this.gtaoPass.denoiseRadius = gtaoParams.denoiseRadius,			// 降噪半径（1-8）
				this.gtaoPass.lumaPhi = gtaoParams.lumaPhi,						// 亮度阀值（1-20）
				this.gtaoPass.depthPhi = gtaoParams.depthPhi,					// 深度阀值(0.5-5)
				this.gtaoPass.output = gtaoParams.output;						// 启用去噪输出
				
				// 默认禁用
				this.gtaoPass.enabled = false;
				this.gtaoPass.renderToScreen = false;
				
				// 添加到合成器
				if (this.composer) {
					this.composer.addPass(this.gtaoPass);
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
				
				this.renderInvalidate();
			}

			updateSSAOParameters() {
				if (!this.ssaoPass) return;
				
				const ssaoParams = this.state.postProcessingParams.ssao;
				
				this.ssaoPass.kernelRadius = ssaoParams.kernelRadius;
				this.ssaoPass.minDistance = ssaoParams.minDistance;
				this.ssaoPass.maxDistance = ssaoParams.maxDistance;
				
				this.renderInvalidate();
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
				this.gtaoPass.denoiseRadius = gtaoParams.denoiseRadius;
				this.gtaoPass.lumaPhi = gtaoParams.lumaPhi;
				this.gtaoPass.depthPhi = gtaoParams.depthPhi;
				
				if (this.gtaoPass.updateGtaoMaterial) {
					const aoParameters = {
						radius: this.gtaoPass.radius,
						distanceExponent: this.gtaoPass.distanceExponent,
						thickness: this.gtaoPass.thickness,
						scale: this.gtaoPass.scale,
						distanceFallOff: this.gtaoPass.distanceFallOff,
						samples: this.gtaoPass.samples,
						screenSpaceRadius: false
					};
					this.gtaoPass.updateGtaoMaterial(aoParameters);
				}
				
				if (this.gtaoPass.updatePdMaterial) {
					const pdParameters = {
						lumaPhi: this.gtaoPass.lumaPhi || 10.0,
						depthPhi: this.gtaoPass.depthPhi || 2.0,
						normalPhi: 3.0,
						radius: this.gtaoPass.denoiseRadius || 4.0,
						radiusExponent: 1.0,
						rings: 2.0,
						samples: 16
					};
					this.gtaoPass.updatePdMaterial(pdParameters);
				}
				
				this.renderInvalidate();
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
				
				const controllers = this.state.materialGUI.contourControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
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
				this.updateSSAOParameters();
				
				const controllers = this.state.materialGUI.ssaoControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
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
					denoiseRadius: 4.0,
					lumaPhi: 10.0,
					depthPhi: 2.0,
					normalPhi: 3.0,
					output: GTAOPass.OUTPUT.Denoise
				};
				
				Object.assign(this.state.postProcessingParams.gtao, defaultGTAOParams);
				this.UpdateGTAOParameters();
				
				const controllers = this.state.materialGUI.gtaoControllers;
				if (controllers) {
					Object.values(controllers).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
				}
			}

			// 材质切换
			handleMatChange(eOrMode) {
				const mode = typeof eOrMode === 'string' 
					? eOrMode 
					: eOrMode.target.value;
				
				const previousMode = this.state.materialMode;
				this.state.materialMode = mode;
				
				if (mode !== 'original') {
					this.hideSelectedMaterialGUI();
				}
				
				if (!this.composer && (mode === 'contour' || mode === 'ssao' || mode === 'gtao')) {
					this.initPostProcessing();
				}
				
				switch (mode) {
					case 'ssao':    this.enableSSAO(); break;
					case 'gtao':    this.enableGTAO(); break;
					case 'contour': this.enableContour(); break;
					default:        this.disablePostProcessing(); break;
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
					this.isContourMode = true;
					
					// 确保轮廓通道启用
					if (this.contourPass) {
						this.contourPass.enabled = true;
					}
				} else {
					this.isContourMode = false;
					
					// 禁用轮廓通道
					if (this.contourPass) {
						this.contourPass.enabled = false;
					}
				}
				
				this.showMaterialFolder(mode);
				this.applyMaterialMode();
				this.updateBgColorPickerState(mode);
				this.toggleLightGUI();
				
				// 当切换回original模式时，如果有选中的对象，显示选中的材质GUI
				if (mode === 'original' && previousMode !== 'original') {
					// 检查是否有选中的对象
					if (this.state.selection.selectedObject && this.state.selection.selectedObject.material) {
						// 延迟一点显示，确保材质已经应用完成
						setTimeout(() => {
							if (this.state.materialMode === 'original' && 
								this.state.selection.selectedObject) {
								this.showSelectedMaterialGUI(this.state.selection.selectedObject);
							}
						}, 50);
					}
				}
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
				
				this.renderInvalidate();
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
				
				this.renderInvalidate();
			}

			saveOriginalMaterials(object) {
				if (!object) return;
				
				object.traverse(child => {
					if (child.isMesh && child.material) {
						// 保存原始材质
						this.state.originalMaterials.set(child, child.material);
						
						// 检查并保存纹理
						const materials = Array.isArray(child.material) ? child.material : [child.material];
						
						materials.forEach((material, index) => {
							if (material) {
								// 检查所有可能的纹理类型
								const textureTypes = ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'emissiveMap', 'aoMap'];
								
								textureTypes.forEach(type => {
									if (material[type] && material[type].isTexture) {
										const texture = material[type];
										// 确保纹理被正确标记以便导出
										if (texture.image) {
											// 如果纹理有外部URL，确保导出器可以处理
											if (texture.image.src && texture.image.src.startsWith('data:')) {
												// Data URL 可以直接嵌入
												texture.userData.isDataURL = true;
											} else if (texture.image.src) {
												// 外部URL，确保在导出时嵌入
												texture.userData.originalURL = texture.image.src;
											}
										}
										
										// 保存纹理引用
										this.state.originalTextures.set(child.uuid + "_" + type + "_" + index, texture);
									}
								});
							}
						});
					}
				});
			}

			collectTexturesFromMaterial(material, textureMap, mesh) {
				// 检查传入的是否是有效材质
				if (!material) {
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
					light.castShadow = this.state.lights.shadowsEnabled;
					light.shadow.needsUpdate = true;
					
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
				const farClip = parseFloat((maxDimension * 3).toFixed(2));
				this.state.lights.shadowSettings.camera.near = nearClip;
				this.state.lights.shadowSettings.camera.far = farClip;
				
				// 5. 更新球面坐标显示
				this.updateDirLightSphericalGUI();
				
				// 6. 灯光设置
				dirLight.castShadow = this.state.lights.shadowsEnabled;
				this.updateShadowSettings();
				this.updateDirLightGUI('shadow');
				
				// 7. 更新灯光可视化位置
				if (dirLight.userData.sphereVisualization) {
					dirLight.userData.sphereVisualization.position.copy(dirLight.position);
				}
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
					light.shadow.normalBias = this.state.lights.shadowSettings.normalBias;
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
					light.shadow.normalBias = this.state.lights.shadowSettings.normalBias;
					
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
				
				this.state.commonParams.side = 'front';
				if (this.dom.inputs.sideSelect) {
					this.dom.inputs.sideSelect.value = 'Front';
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
				this.renderInvalidate();
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
				this.renderInvalidate();
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
				this.renderInvalidate();
			}

			updateAmbLightColor() {
				if (this.state.lights.amb) {
					this.state.lights.amb.color.set(this.state.lights.ambColor);
				}
				this.renderInvalidate();
			}

			updateDirLightIntensity() {
				if (!this.state.useSceneLight && this.state.lights.dir) {
					this.state.lights.dir.intensity = this.state.lights.dirIntensity;
				}
				this.renderInvalidate();
			}

			updateAmbLightIntensity() {
				if (!this.state.useSceneLight && this.state.lights.amb) {
					this.state.lights.amb.intensity = this.state.lights.ambIntensity;
				}
				this.renderInvalidate();
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
				this.renderInvalidate();
			}

			updateShadowType() {
				const shadowType = this.state.lights.shadowSettings.shadowTypes[this.state.lights.shadowSettings.shadowType];
				if (shadowType && this.renderer) {
					this.renderer.shadowMap.type = shadowType;
				}
				this.renderInvalidate();
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
				/* this.state.lights.scene.forEach(light => {
					if (light.castShadow) {
						this.configureLightShadows(light);
					}
				}); */
				this.renderInvalidate();
			}

			updateDirLightGUI(updateType = 'all') {
				const controllers = this.state.lightGUI.dirLightControllers;
				const updateTypes = updateType.toLowerCase().split(',').map(t => t.trim());
				
				updateTypes.forEach(type => {
					
					switch(type) {
						case 'main':
							// 重置颜色和强度
							if (controllers) {
								if (controllers.color) controllers.color.updateDisplay();
								if (controllers.intensity) controllers.intensity.updateDisplay();
							}
							break;
							
						case 'pose':
							// 重置球面坐标
							if (controllers && controllers.pose) {
								Object.values(controllers.pose).forEach(controller => {
									if (controller) {
										controller.updateDisplay();
									}
								});
							}
							break;
							
						case 'shadow':
							// 重置阴影设置
							if (controllers && controllers.shadow) {
								Object.values(controllers.shadow).forEach(controller => {
									if (controller) {
										controller.updateDisplay();
									}
								});
							}
							break;
							
						case 'all':
							// 重置所有
							this.updateDirLightGUI('main,pose,shadow');
							break;
					}
				});
			}

			updateDirLightSphericalGUI() {
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
				
				const controllers = this.state.lightGUI.dirLightControllers;
				if (controllers && controllers.pose) {
					Object.values(controllers.pose).forEach(controller => {
						if (controller) {
							controller.updateDisplay();
						}
					});
				}
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
				
				const controllers = this.state.lightGUI.dirLightControllers;
				const resetTypes = resetType.toLowerCase().split(',').map(t => t.trim());
				
				resetTypes.forEach(type => {
					
					switch(type) {
						case 'main':
							// 重置颜色和强度
							this.state.lights.dirColor = defaultMainParams.dirColor;
							this.state.lights.dirIntensity = defaultMainParams.dirIntensity;
							this.updateDirLightColor();
							this.updateDirLightIntensity();
							this.updateDirLightGUI('main');
							break;
							
						case 'pose':
							// 重置球面坐标
							Object.assign(this.state.lights.dirSpherical, defaultPoseParams.dirSpherical);
							this.updateDirLightFromSpherical();
							this.updateDirLightGUI('pose');
							break;
							
						case 'shadow':
							// 重置阴影设置
							const { camera, ...otherShadowSettings } = defaultShadowParams;
							Object.assign(this.state.lights.shadowSettings, otherShadowSettings);
							Object.assign(this.state.lights.shadowSettings.camera, camera);
							this.updateShadowType();
							this.updateShadowSettings();
							this.updateDirLightGUI('shadow');
							break;
							
						case 'all':
							// 重置所有
							this.resetDirLightParameters('main,pose,shadow');
							break;
					}
				});
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
				
				if (this.state.lightGUI.ambLightControllers) {
					this.state.lightGUI.ambLightControllers.color.updateDisplay();
					this.state.lightGUI.ambLightControllers.intensity.updateDisplay();
				}
			}

			// BBox & Center & Focus
			initAnimationBBoxData() {
				const totalFrames = this.state.playback.totalFrames;
				const animationBBoxData = this.state.animationBBoxData;
				
				// 如果已经初始化且有导入数据，跳过
				if (animationBBoxData.isInitialized && 
					animationBBoxData.sampledFrames && 
					animationBBoxData.sampledFrames.size > 0) {
					return;
				}
				
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
					// 如果已经有导入的数据，使用它
					if (animationBBoxData.sampledFrames && animationBBoxData.sampledFrames.size > 0) {
						animationBBoxData.isInitialized = true;
					} else {
						this.initAnimationBBoxData();
					}
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

			serializeAnimationBBoxData() {
				const data = this.state.animationBBoxData;
				
				const serialized = {
					sampledFrames: {},
					sampleFrameNumbers: [...data.sampleFrameNumbers],
					samplingInterval: data.samplingInterval,
					isInitialized: data.isInitialized,
					hasAnimation: data.hasAnimation,
					aggregated: {
						overallMin: data.aggregated.overallMin ? data.aggregated.overallMin.toArray() : null,
						overallMax: data.aggregated.overallMax ? data.aggregated.overallMax.toArray() : null,
						averageCenter: data.aggregated.averageCenter ? data.aggregated.averageCenter.toArray() : null,
						overallSize: data.aggregated.overallSize ? data.aggregated.overallSize.toArray() : null
					}
				};
				
				// 序列化采样帧数据
				data.sampledFrames.forEach((frameData, frame) => {
					serialized.sampledFrames[frame] = {
						min: frameData.min ? frameData.min.toArray() : null,
						max: frameData.max ? frameData.max.toArray() : null,
						center: frameData.center ? frameData.center.toArray() : null,
						size: frameData.size ? frameData.size.toArray() : null,
						isEmpty: frameData.isEmpty
					};
				});
				
				// 序列化缓存帧数据
				serialized.cachedFrames = {};
				data.cachedFrames.forEach((frameData, frame) => {
					serialized.cachedFrames[frame] = {
						min: frameData.min ? frameData.min.toArray() : null,
						max: frameData.max ? frameData.max.toArray() : null,
						center: frameData.center ? frameData.center.toArray() : null,
						size: frameData.size ? frameData.size.toArray() : null,
						isEmpty: frameData.isEmpty
					};
				});
				
				return serialized;
			}

			deserializeAnimationBBoxData(serializedData) {
				const bboxData = {
					sampledFrames: new Map(),
					aggregated: {
						overallMin: serializedData.aggregated.overallMin ? 
							new THREE.Vector3().fromArray(serializedData.aggregated.overallMin) : null,
						overallMax: serializedData.aggregated.overallMax ? 
							new THREE.Vector3().fromArray(serializedData.aggregated.overallMax) : null,
						averageCenter: serializedData.aggregated.averageCenter ? 
							new THREE.Vector3().fromArray(serializedData.aggregated.averageCenter) : null,
						overallSize: serializedData.aggregated.overallSize ? 
							new THREE.Vector3().fromArray(serializedData.aggregated.overallSize) : null
					},
					cachedFrames: new Map(),
					sampleFrameNumbers: serializedData.sampleFrameNumbers || [],
					samplingInterval: serializedData.samplingInterval || 25,
					isInitialized: serializedData.isInitialized || false,
					hasAnimation: serializedData.hasAnimation || false
				};
				
				// 恢复采样帧数据
				if (serializedData.sampledFrames) {
					Object.keys(serializedData.sampledFrames).forEach(frame => {
						const frameData = serializedData.sampledFrames[frame];
						bboxData.sampledFrames.set(parseInt(frame), {
							min: frameData.min ? new THREE.Vector3().fromArray(frameData.min) : null,
							max: frameData.max ? new THREE.Vector3().fromArray(frameData.max) : null,
							center: frameData.center ? new THREE.Vector3().fromArray(frameData.center) : null,
							size: frameData.size ? new THREE.Vector3().fromArray(frameData.size) : null,
							isEmpty: frameData.isEmpty || false
						});
					});
				}
				
				// 恢复缓存帧数据
				if (serializedData.cachedFrames) {
					Object.keys(serializedData.cachedFrames).forEach(frame => {
						const frameData = serializedData.cachedFrames[frame];
						bboxData.cachedFrames.set(parseInt(frame), {
							min: frameData.min ? new THREE.Vector3().fromArray(frameData.min) : null,
							max: frameData.max ? new THREE.Vector3().fromArray(frameData.max) : null,
							center: frameData.center ? new THREE.Vector3().fromArray(frameData.center) : null,
							size: frameData.size ? new THREE.Vector3().fromArray(frameData.size) : null,
							isEmpty: frameData.isEmpty || false
						});
					});
				}
				
				return bboxData;
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
				let bboxData;
				let targetName = '';
				
				if (this.state.selection.isSelecting && this.state.selection.selectedObject) {
					const selectedObject = this.state.selection.selectedObject;
					targetName = selectedObject.name || 'Selected Mesh';
					
					// 计算选中物体的包围盒
					const box = new THREE.Box3().setFromObject(selectedObject);
					if (!box.isEmpty()) {
						const center = new THREE.Vector3();
						const size = new THREE.Vector3();
						box.getCenter(center);
						box.getSize(size);
						
						bboxData = {
							center: center.clone(),
							size: size.clone(),
							min: box.min.clone(),
							max: box.max.clone(),
							isEmpty: false
						};
						
					} else {
						// 选中物体为空，使用场景
						bboxData = this.getBBoxForCurrentFrame();
						targetName = 'Scene';
					}
				} else {
					// 没有选中物体，使用场景
					bboxData = this.getBBoxForCurrentFrame();
					targetName = 'Scene';
				}
				
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
				this.renderInvalidate();
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
				let bboxData;
				let targetName = '';
				
				// 2. 检查是否有选中的物体
				if (this.state.selection.isSelecting && this.state.selection.selectedObject) {
					const selectedObject = this.state.selection.selectedObject;
					targetName = selectedObject.name || 'Selected Mesh';
					
					// 计算选中物体的包围盒
					const box = new THREE.Box3().setFromObject(selectedObject);
					if (!box.isEmpty()) {
						const center = new THREE.Vector3();
						const size = new THREE.Vector3();
						box.getCenter(center);
						box.getSize(size);
						
						bboxData = {
							center: center.clone(),
							size: size.clone(),
							min: box.min.clone(),
							max: box.max.clone(),
							isEmpty: false
						};
					} else {
						// 选中物体为空，使用场景
						bboxData = this.getBBoxForCurrentFrame();
						targetName = 'Scene';
					}
				} else {
					// 没有选中物体，使用场景
					bboxData = this.getBBoxForCurrentFrame();
					targetName = 'Scene';
				}
				
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
				
				this.renderInvalidate();
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
				// 如果是选中的物体，永远不要排除
				if (this.state.selection.selectedObject === object) {
					return false;
				}
				
				// 检查选中的物体是否在父级链中
				let parent = object.parent;
				while (parent) {
					if (parent === this.state.selection.selectedObject) {
						return false; // 如果对象是选中物体的子对象，不要排除
					}
					parent = parent.parent;
				}
				
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
				this.renderInvalidate();
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
				this.renderInvalidate();
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
				
				// 更新其他UI
				this.updateOrthoToggleState();
				this.updateCameraUIForMode();
				this.updateKeyframeButtonsState();
				this.updateAutoAddKeyframeButtonState();
				this.updateVisualizationVisibility();
				this.updateKeyframeCount();
				this.updatePostProcessing();
				
				// 保证切换到正交相机时获得正确aspect ratio
				// 其中包含了 renderInvalidate
				this.onWindowResize();
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
				this.renderInvalidate();
				
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
				this.renderInvalidate();
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
				
				setTimeout(() => {
					this.updateCameraUIForMode();
					this.renderInvalidate();
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
				const shouldDisable = this.state.controlsDisabled || isSceneCamera || isCustomCameraWithAnim || isCustomCameraWithKeyframes;
				
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
					
					// 如果全局禁用，强制设为禁用状态
					if (this.state.controlsDisabled) {
						button.disabled = true;
						button.classList.remove('enabled-control');
						button.classList.add('disabled-control');
						return;
					}
					
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
				const isSceneCamera = !this.state.controlsDisabled && this.state.cameras.currentType === 'scene';
				const isCameraAnimEnabled = !this.state.controlsDisabled && this.state.cameras.currentType === 'custom' && this.state.cameraAnim.isEnabled;
				
				const setEnabled = (el, enabled) => {
					if (!el) return;
					
					// 如果全局禁用，强制设为禁用状态
					if (this.state.controlsDisabled) {
						el.classList.add('disabled-control');
						el.classList.remove('enabled-control');
						el.disabled = true;
						return;
					}
					
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
				this.renderInvalidate();
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
				this.renderInvalidate();
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
				this.renderInvalidate();
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
					
					// 如果全局禁用，强制设为禁用状态
					if (this.state.controlsDisabled) {
						el.disabled = true;
						el.classList.add('disabled-control');
						el.classList.remove('enabled-control');
						return;
					}
					
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
				this.renderInvalidate();
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

			// 场景诊断
			sceneDiagnostics() {
				console.log("=== Scene Diagnostics Start ===");
				
				// ============== 收集所有信息 ==============
				const objectInfo = this.collectObjectInfo();
				const materialTextureInfo = this.collectMaterialAndTextureInfo();
				const lightInfo = this.collectLightInfo();
				const cameraInfo = this.collectCameraInfo();
				const animationInfo = this.collectAnimationInfo();
				
				// 计算材质汇总
				const materialSummary = this.calculateMaterialSummary(
					materialTextureInfo.materials, 
					materialTextureInfo.textures
				);
				
				// ============== 汇总数据 ==============
				this.printSceneSummary(objectInfo, materialTextureInfo, lightInfo, cameraInfo, animationInfo);
				
				// ============== 场景物体分析 ==============
				this.printObjectAnalysis(objectInfo);
				
				// ============== 几何体分析 ==============
				this.printGeometryAnalysis(objectInfo.geometryInfo);
				
				// ============== 材质分析 ==============
				this.printMaterialAnalysis(materialTextureInfo, materialSummary);
				
				// ============== 纹理分析 ==============
				this.printTextureAnalysis(materialTextureInfo, materialSummary);
				
				// ============== 灯光分析 ==============
				this.printLightAnalysis(lightInfo);
				
				// ============== 相机分析 ==============
				this.printCameraAnalysis(cameraInfo);
				
				// ============== 动画信息 ==============
				this.printAnimationAnalysis(animationInfo);
				
				console.log("=== Scene Diagnostics Complete ===");
				this.showMessage("Please check the console for detailed diagnostics.", 5000);
			}

			printSceneSummary(objectInfo, materialTextureInfo, lightInfo, cameraInfo, animationInfo) {
				console.group("Scene Summary");
				console.log("Objects: " + objectInfo.objectStats.total + " (Visible: " + objectInfo.objectStats.visible + ")");
				console.log("Geometry: " + objectInfo.geometryInfo.vertices.toLocaleString() + " vertices, " + 
					objectInfo.geometryInfo.triangles.toLocaleString() + " triangles");
				console.log("Materials: " + materialTextureInfo.materialMap.size + ", Textures: " + materialTextureInfo.textureMap.size);
				console.log("Lights: " + lightInfo.totalLights + " (With shadows: " + lightInfo.shadowEnabledLights + ")");
				console.log("Cameras: " + cameraInfo.totalCameras + 
					" (Default: " + cameraInfo.defaultCameras.length + 
					", Custom: " + cameraInfo.customCameras.length + 
					", Scene: " + cameraInfo.sceneCameras.length + 
					", Animated: " + cameraInfo.cameras.filter(cam => cam.hasAnimation).length + ")");
				console.log("Animations: " + animationInfo.totalClips + " clip(s)");
				console.groupEnd();
			}

			printObjectAnalysis(objectInfo) {
				console.groupCollapsed("Scene Object Overview:");
				console.log("Total objects: " + objectInfo.objectStats.total);
				console.log("Visible objects: " + objectInfo.objectStats.visible);
				console.log("Groups: " + objectInfo.objectStats.groups);
				console.log("Meshes: " + objectInfo.objectStats.meshes);
				console.log("Lines: " + objectInfo.objectStats.lines);
				console.log("Points: " + objectInfo.objectStats.points);
				
				// 类型分析
				console.groupCollapsed("Object type distribution:");
				for (var type in objectInfo.objectStats.types) {
					if (objectInfo.objectStats.types.hasOwnProperty(type)) {
						console.log(type + ": " + objectInfo.objectStats.types[type]);
					}
				}
				console.groupEnd();
				
				// 物体详细信息
				console.groupCollapsed("Detailed Object Information:");
				for (const objName in objectInfo.objects) {
					const obj = objectInfo.objects[objName];
					console.groupCollapsed("Object: " + objName);
					this.printObjectDetails(obj);
					console.groupEnd();
				}
				console.groupEnd();
				
				console.groupEnd(); // Scene Object Overview group
			}

			printGeometryAnalysis(geometryInfo) {
				console.groupCollapsed("Geometry Statistics:");
				console.log("Total vertices: " + geometryInfo.vertices.toLocaleString());
				console.log("Total faces: " + geometryInfo.faces.toLocaleString());
				console.log("Total triangles: " + geometryInfo.triangles.toLocaleString());
				
				// 按对象类型显示几何体信息
				console.groupCollapsed("Geometry by object type:");
				const geometryByType = {
					Meshes: { vertices: 0, faces: 0, triangles: 0, count: 0 },
					Lines: { vertices: 0, segments: 0, count: 0 },
					Points: { vertices: 0, count: 0 }
				};
				
				for (const objName in geometryInfo.byObject) {
					const objInfo = geometryInfo.byObject[objName];
					
					if (objInfo.type === "Mesh") {
						geometryByType.Meshes.vertices += objInfo.vertices;
						geometryByType.Meshes.faces += objInfo.faces;
						geometryByType.Meshes.triangles += objInfo.triangles;
						geometryByType.Meshes.count++;
					} else if (objInfo.type === "Line") {
						geometryByType.Lines.vertices += objInfo.vertices;
						geometryByType.Lines.segments += (objInfo.segments || 0);
						geometryByType.Lines.count++;
					} else if (objInfo.type === "Points") {
						geometryByType.Points.vertices += objInfo.vertices;
						geometryByType.Points.count++;
					}
				}
				
				console.groupCollapsed("Meshes: " + geometryByType.Meshes.count);
				console.log("Vertices: " + geometryByType.Meshes.vertices.toLocaleString());
				console.log("Faces: " + geometryByType.Meshes.faces.toLocaleString());
				console.log("Triangles: " + geometryByType.Meshes.triangles.toLocaleString());
				console.log("Average vertices per mesh: " + 
					(geometryByType.Meshes.count > 0 ? 
						Math.round(geometryByType.Meshes.vertices / geometryByType.Meshes.count) : 0));
				console.groupEnd();
				
				if (geometryByType.Lines.count > 0) {
					console.groupCollapsed("Lines: " + geometryByType.Lines.count);
					console.log("Vertices: " + geometryByType.Lines.vertices.toLocaleString());
					console.log("Segments: " + geometryByType.Lines.segments.toLocaleString());
					console.groupEnd();
				}
				
				if (geometryByType.Points.count > 0) {
					console.groupCollapsed("Points: " + geometryByType.Points.count);
					console.log("Vertices: " + geometryByType.Points.vertices.toLocaleString());
					console.groupEnd();
				}
				
				console.groupEnd(); // Geometry by object type
				console.groupEnd(); // Geometry Statistics group
			}

			printMaterialAnalysis(materialTextureInfo, materialSummary) {
				console.groupCollapsed("Material Statistics:");
				console.log("Total unique materials: " + materialTextureInfo.materialMap.size);
				console.log("Material types: " + JSON.stringify(materialSummary.materialsByType, null, 2));
				
				// 按材质名称分组，显示同名材质数量
				const materialsByName = new Map();
				materialTextureInfo.materialMap.forEach((matInfo, materialId) => {
					const matName = matInfo.name;
					if (!materialsByName.has(matName)) {
						materialsByName.set(matName, {
							count: 0,
							materials: []
						});
					}
					const group = materialsByName.get(matName);
					group.count++;
					group.materials.push(matInfo);
				});
				
				// 显示材质名称分组统计
				console.groupCollapsed("Materials by name:");
				materialsByName.forEach((group, matName) => {
					if (group.count > 1) {
						console.log(matName + ": " + group.count + " instances (shared material)");
					} else {
						console.log(matName + ": " + group.count + " instance");
					}
				});
				console.groupEnd();
				
				// 显示每个材质的详细信息
				let materialIndex = 1;
				
				// 按材质名称排序，使同名材质相邻显示
				const sortedMaterials = Array.from(materialTextureInfo.materialMap.values())
					.sort((a, b) => a.name.localeCompare(b.name));
				
				sortedMaterials.forEach((matInfo) => {
					// 显示材质实例数量信息
					let title = "Material " + materialIndex + ": " + matInfo.name;
					const group = materialsByName.get(matInfo.name);
					if (group && group.count > 1) {
						title += " (shared, " + group.count + " instances)";
					}
					
					console.groupCollapsed(title);
					this.printMaterialDetails(matInfo, materialTextureInfo);
					console.groupEnd();
					materialIndex++;
				});
				console.groupEnd(); // Materials group
			}

			printTextureAnalysis(materialTextureInfo, materialSummary) {
				console.groupCollapsed("Texture Statistics:");
				console.log("Unique textures: " + materialTextureInfo.textureMap.size);
				console.log("Total texture references: " + materialSummary.textureReuseStats.totalTextureReferences);
				console.log("Average reuse: " + materialSummary.textureReuseStats.averageReuse + " references per texture");
				console.log("Texture usage by channel: " + JSON.stringify(materialSummary.texturesByType, null, 2));
				
				// 显示每个纹理的详细信息
				let textureIndex = 1;
				materialTextureInfo.textureMap.forEach((texInfo, textureId) => {
					console.groupCollapsed("Texture " + textureIndex + ": " + texInfo.channels.join(", "));
					this.printTextureDetails(texInfo, materialTextureInfo);
					console.groupEnd();
					textureIndex++;
				});
				console.groupEnd(); // Texture Statistics group
			}

			printLightAnalysis(lightInfo) {
				console.groupCollapsed("Light Statistics:");
				console.log("Total lights: " + lightInfo.totalLights);
				console.log("Shadow enabled globally: " + lightInfo.shadowSettings.enabled);
				console.log("Shadow map type: " + this.getShadowMapTypeName(lightInfo.shadowSettings.shadowMapType));
				console.log("Shadow map auto-update: " + lightInfo.shadowSettings.shadowMapAutoUpdate);
				
				// 灯光类型分布
				console.groupCollapsed("Light type distribution:");
				for (const type in lightInfo.lightsByType) {
					console.log(type + ": " + lightInfo.lightsByType[type]);
				}
				console.groupEnd();	// Light type group
				
				// 阴影统计
				console.groupCollapsed("Shadow Statistics:");
				console.log("Lights with shadows: " + lightInfo.shadowEnabledLights + " / " + lightInfo.totalLights);
				console.log("Shadow map type: " + this.getShadowMapTypeName(this.renderer.shadowMap.type));
				
				// 修复：检查this.state.lights是否存在
				if (this.state.lights) {
					console.log("Default shadow settings:");
					console.log("  Map size: " + this.state.lights.shadowSettings.mapSize + "x" + this.state.lights.shadowSettings.mapSize);
					console.log("  Bias: " + this.state.lights.shadowSettings.bias);
					console.log("  Normal bias: " + this.state.lights.shadowSettings.normalBias);
					console.log("  Radius: " + this.state.lights.shadowSettings.radius);
				} else {
					console.log("Default shadow settings: Not available");
				}
				console.groupEnd();	// shadow group
				
				// 详细灯光信息
				console.groupCollapsed("Detailed Light Information:");
				lightInfo.lights.forEach(light => {
					console.groupCollapsed("Light " + light.id + ": " + light.name);
					this.printLightDetails(light);
					console.groupEnd(); // Light group
				});
				console.groupEnd(); // Detailed Light Information
				console.groupEnd(); // Light Statistics group
			}

			printCameraAnalysis(cameraInfo) {
				console.groupCollapsed("Camera Statistics:");
				console.log("Total cameras: " + cameraInfo.totalCameras);
				console.log("Current camera type: " + cameraInfo.currentCameraType);
				console.log("Active camera: " + (cameraInfo.activeCamera ? cameraInfo.activeCamera.name : 'None'));
				
				console.groupCollapsed("Camera distribution:");
				console.log("Default cameras: " + cameraInfo.defaultCameras.length);
				console.log("Custom cameras: " + cameraInfo.customCameras.length);
				console.log("Scene cameras: " + cameraInfo.sceneCameras.length);
				console.log("Projection types:");
				console.log("  Perspective: " + (cameraInfo.camerasByType.perspective || 0));
				console.log("  Orthographic: " + (cameraInfo.camerasByType.orthographic || 0));
				console.groupEnd();	// camera distribution group
				
				if (cameraInfo.activeCamera) {
					console.groupCollapsed("Active Camera Details:");
					this.printCameraDetails(cameraInfo.activeCamera, true);
					console.groupEnd();	// active camera group
				}
				
				const animatedCameras = cameraInfo.cameras.filter(cam => cam.hasAnimation);
				console.groupCollapsed("Camera Animation Statistics:");
				console.log("Animated cameras: " + animatedCameras.length + " / " + cameraInfo.totalCameras);
				animatedCameras.forEach(cam => {
					console.log("  " + cam.name + ": " + cam.keyframeCount + " keyframes");
				});
				console.groupEnd();	// camera animation group
				
				if (cameraInfo.orbitControlsInfo) {
					console.groupCollapsed("Orbit Controls Settings:");
					const controls = cameraInfo.orbitControlsInfo;
					this.printOrbitControlsDetails(controls);
					console.groupEnd();	// orbit control group
				}
				
				console.groupCollapsed("Detailed Camera Information:");
				cameraInfo.cameras.forEach((cam, index) => {
					console.groupCollapsed("Camera " + (index + 1) + ": " + cam.name + " (" + cam.category + ")");
					this.printCameraDetails(cam, false);
					console.groupEnd();	// detail camera group
				});
				console.groupEnd();	// detail cameras group
				console.groupEnd(); // Camera Statistics group
			}

			printAnimationAnalysis(animationInfo) {
				console.groupCollapsed("Animation Statistics:");
				
				if (animationInfo.totalClips > 0) {
					console.log("Animation clips: " + animationInfo.totalClips);
					console.log("Total tracks: " + animationInfo.totalTracks);
					console.log("Total keyframes: " + animationInfo.totalKeyframes);
					console.log("Animated objects: " + animationInfo.animatedObjects.length);
					
					// 播放信息
					console.groupCollapsed("Playback Info:");
					console.log("FPS: " + animationInfo.playbackInfo.fps);
					console.log("Total frames: " + animationInfo.playbackInfo.totalFrames);
					console.log("Current frame: " + animationInfo.playbackInfo.currentFrame);
					console.log("Is playing: " + animationInfo.playbackInfo.isPlaying);
					console.log("Loop mode: " + animationInfo.playbackInfo.loopMode);
					console.log("Speed: " + animationInfo.playbackInfo.speed);
					console.log("Time scale: " + animationInfo.playbackInfo.timeScale);
					console.groupEnd();
					
					// 混合器信息（如果有）
					if (animationInfo.mixerInfo) {
						console.groupCollapsed("Animation Mixer:");
						console.log("Mixer time: " + animationInfo.mixerInfo.time.toFixed(2));
						console.log("Time scale: " + animationInfo.mixerInfo.timeScale);
						console.log("Active actions: " + animationInfo.mixerInfo.activeActionsCount);
						console.log("Total roots: " + animationInfo.mixerInfo.totalRoots);
						
						// 检查是否有统计信息
						if (animationInfo.mixerInfo.statistics) {
							console.log("Total duration: " + animationInfo.mixerInfo.statistics.totalDuration.toFixed(2) + "s");
							console.log("Average duration: " + animationInfo.mixerInfo.statistics.averageDuration.toFixed(2) + "s");
							console.log("Max duration: " + animationInfo.mixerInfo.statistics.maxDuration.toFixed(2) + "s");
						}
						console.groupEnd();
					}
					
					// 动画统计
					console.groupCollapsed("Animation Statistics:");
					console.log("Total duration: " + animationInfo.statistics.totalDuration.toFixed(2) + "s");
					console.log("Average duration: " + animationInfo.statistics.averageDuration.toFixed(2) + "s");
					console.log("Max duration: " + animationInfo.statistics.maxDuration.toFixed(2) + "s");
					
					console.log("By duration:");
					console.log("  Short (<2s): " + animationInfo.clipStatistics.byDuration.short);
					console.log("  Medium (2-10s): " + animationInfo.clipStatistics.byDuration.medium);
					console.log("  Long (>10s): " + animationInfo.clipStatistics.byDuration.long);
					
					console.log("By track count:");
					console.log("  Simple (<5 tracks): " + animationInfo.clipStatistics.byTrackCount.simple);
					console.log("  Medium (5-20 tracks): " + animationInfo.clipStatistics.byTrackCount.medium);
					console.log("  Complex (>20 tracks): " + animationInfo.clipStatistics.byTrackCount.complex);
					
					console.log("By property type:");
					for (const propType in animationInfo.clipStatistics.byPropertyType) {
						if (animationInfo.clipStatistics.byPropertyType[propType] > 0) {
							console.log("  " + propType + ": " + animationInfo.clipStatistics.byPropertyType[propType]);
						}
					}
					console.groupEnd();
					
					// 动画剪辑详细信息
					console.groupCollapsed("Animation Clip Details:");
					animationInfo.clips.forEach((clip, index) => {
						console.groupCollapsed("Clip " + (index + 1) + ": " + clip.name);
						this.printAnimationClipDetails(clip);
						console.groupEnd(); // 单个剪辑
					});
					console.groupEnd(); // 动画剪辑详细信息
					
					// 被动画控制的对象详情
					if (animationInfo.animatedObjects.length > 0) {
						console.groupCollapsed("Animated Objects Details:");
						animationInfo.animatedObjects.forEach((obj, index) => {
							console.groupCollapsed("Object " + (index + 1) + ": " + obj.name);
							this.printAnimatedObjectDetails(obj);
							console.groupEnd();
						});
						console.groupEnd();
					}
				} else {
					console.log("Animation clips: None");
				}
				
				console.groupEnd(); // Animation Information group
			}

			printObjectDetails(obj) {
				console.log("Type: " + obj.type);
				console.log("Visible: " + obj.visible);
				console.log("Position: [" + obj.position.join(", ") + "]");
				console.log("Has animation: " + (obj.hasAnimation ? "Yes" : "No"));
				if (obj.animationInfo) {
					console.log("Animation frames: " + obj.animationInfo.keyframeCount);
					console.log("Animation duration: " + obj.animationInfo.duration.toFixed(2) + "s");
				}
				if (obj.userDataKeys && obj.userDataKeys.length > 0) {
					console.log("User data keys: " + obj.userDataKeys.join(", "));
				}
			}

			printMaterialDetails(matInfo, materialTextureInfo) {
				console.log("Type: " + matInfo.type);
				console.log("UUID: " + matInfo.uuid);
				console.log("Used by " + matInfo.objectCount + " object(s):");
				
				// 显示使用此材质的物体名称
				if (matInfo.objectNames && matInfo.objectNames.length > 0) {
					console.groupCollapsed("Objects using this material:");
					matInfo.objectNames.forEach((objName, index) => {
						console.log((index + 1) + ". " + objName);
					});
					console.groupEnd();
				}
				
				console.log("Textures: " + matInfo.textureCount);
				
				if (matInfo.textureCount > 0) {
					console.groupCollapsed("Textures (" + matInfo.textureCount + "):");
					for (const texType in matInfo.textures) {
						const texData = matInfo.textures[texType];
						console.log(texType + ":");
						console.log("  UUID: " + texData.uuid);
						console.log("  Source: " + texData.source);
						
						// 检查这个纹理是否被其他通道复用
						const texInfo = materialTextureInfo.textureMap.get(texData.uuid);
						if (texInfo && texInfo.channels.length > 1) {
							const otherChannels = texInfo.channels.filter(ch => ch !== texType);
							if (otherChannels.length > 0) {
								console.log("  Also used as: " + otherChannels.join(", "));
							}
						}
					}
					console.groupEnd();
				}
				
				console.groupCollapsed("Properties:");
				console.log("  Color: #" + matInfo.properties.color);
				console.log("  Roughness: " + matInfo.properties.roughness);
				console.log("  Metalness: " + matInfo.properties.metalness);
				console.log("  Emissive: #" + matInfo.properties.emissive);
				console.log("  Emissive Intensity: " + matInfo.properties.emissiveIntensity);
				console.log("  Opacity: " + matInfo.properties.opacity);
				console.log("  Transparent: " + matInfo.properties.transparent);
				console.log("  Bump Scale: " + matInfo.properties.bumpScale);
				console.log("  Normal Scale: X=" + matInfo.properties.normalScale.x + ", Y=" + matInfo.properties.normalScale.y);
				console.log("  Displacement Scale: " + matInfo.properties.displacementScale);
				console.log("  Displacement Bias: " + matInfo.properties.displacementBias);
				console.log("  AO Map Intensity: " + matInfo.properties.aoMapIntensity);
				console.log("  Side: " + matInfo.properties.side);
				console.log("  Wireframe: " + matInfo.properties.wireframe);
				console.log("  Flat Shading: " + matInfo.properties.flatShading);
				
				// 其他材质属性
				if (matInfo.properties.specular !== 'N/A') {
					console.log("  Specular: #" + matInfo.properties.specular);
				}
				if (matInfo.properties.shininess !== 30.0) {
					console.log("  Shininess: " + matInfo.properties.shininess);
				}
				if (matInfo.properties.refractionRatio !== 0.98) {
					console.log("  Refraction Ratio: " + matInfo.properties.refractionRatio);
				}
				if (matInfo.properties.reflectivity !== 1.0) {
					console.log("  Reflectivity: " + matInfo.properties.reflectivity);
				}
				
				// 透明和渲染属性
				if (matInfo.properties.alphaTest > 0) {
					console.log("  Alpha Test: " + matInfo.properties.alphaTest);
				}
				if (!matInfo.properties.depthTest) {
					console.log("  Depth Test: " + matInfo.properties.depthTest);
				}
				if (!matInfo.properties.depthWrite) {
					console.log("  Depth Write: " + matInfo.properties.depthWrite);
				}
				if (matInfo.properties.polygonOffset) {
					console.log("  Polygon Offset: Factor=" + matInfo.properties.polygonOffsetFactor + 
								", Units=" + matInfo.properties.polygonOffsetUnits);
				}
				console.groupEnd();	// Properties group
			}

			printTextureDetails(texInfo, materialTextureInfo) {
				console.log("UUID: " + texInfo.uuid);
				console.log("Source: " + texInfo.source);
				console.log("Size: " + texInfo.size);
				console.log("Format: " + texInfo.format);
				console.log("Wrap S/T: " + texInfo.wrapS + "/" + texInfo.wrapT);
				console.log("Encoding: " + this.getTextureEncodingName(texInfo.encoding));
				
				// 显示UV变换属性
				if (texInfo.repeat && (texInfo.repeat.x !== 1 || texInfo.repeat.y !== 1)) {
					console.log("Repeat: X=" + texInfo.repeat.x + ", Y=" + texInfo.repeat.y);
				}
				if (texInfo.offset && (texInfo.offset.x !== 0 || texInfo.offset.y !== 0)) {
					console.log("Offset: X=" + texInfo.offset.x + ", Y=" + texInfo.offset.y);
				}
				if (texInfo.rotation !== 0) {
					console.log("Rotation: " + texInfo.rotation + " radians");
				}
				if (texInfo.anisotropy !== 1) {
					console.log("Anisotropy: " + texInfo.anisotropy);
				}
				
				console.log("Used by " + texInfo.usedByMaterials.length + " material(s):");
				
				texInfo.usedByMaterials.forEach(usage => {
					const matInfo = materialTextureInfo.materialMap.get(usage.materialId);
					const matName = matInfo ? matInfo.name : usage.materialId;
					console.log("  - " + matName + " (" + usage.channels.join(", ") + ")");
				});
			}

			printLightDetails(light) {
				console.log("Type: " + light.type);
				console.log("UUID: " + light.uuid);
				console.log("Position: [" + light.position.join(", ") + "]");
				console.log("Color: #" + light.color);
				console.log("Intensity: " + light.intensity);
				console.log("Visible: " + light.visible);
				console.log("Casts shadow: " + light.castShadow);
				console.log("Has animation: " + (light.hasAnimation ? "Yes" : "No"));
				if (light.animationInfo) {
					console.log("Animation frames: " + light.animationInfo.keyframeCount);
				}
				
				// 特定灯光属性
				if (Object.keys(light.specificProperties).length > 0) {
					console.groupCollapsed("Specific properties:");
					for (const prop in light.specificProperties) {
						if (Array.isArray(light.specificProperties[prop])) {
							console.log(prop + ": [" + light.specificProperties[prop].join(", ") + "]");
						} else {
							console.log(prop + ": " + light.specificProperties[prop]);
						}
					}
					console.groupEnd();	// specific prop group
				}
				
				// 阴影信息 - 修复：检查shadowInfo是否存在
				console.groupCollapsed("Shadow settings:");
				if (light.shadowInfo) {
					console.log("Enabled: " + light.shadowInfo.enabled);
					
					if (light.shadowInfo.enabled && light.castShadow) {
						console.log("Map size: " + light.shadowInfo.mapSize.width + "x" + light.shadowInfo.mapSize.height);
						console.log("Bias: " + light.shadowInfo.bias);
						console.log("Normal bias: " + light.shadowInfo.normalBias);
						console.log("Radius: " + light.shadowInfo.radius);
						console.log("Blur samples: " + light.shadowInfo.blurSamples);
						
						if (light.shadowInfo.camera) {
							console.groupCollapsed("Shadow camera:");
							console.log("Type: " + light.shadowInfo.camera.type);
							console.log("Near: " + light.shadowInfo.camera.near);
							console.log("Far: " + light.shadowInfo.camera.far);
							
							if (light.shadowInfo.camera.left !== undefined) {
								console.log("Left: " + light.shadowInfo.camera.left);
								console.log("Right: " + light.shadowInfo.camera.right);
								console.log("Top: " + light.shadowInfo.camera.top);
								console.log("Bottom: " + light.shadowInfo.camera.bottom);
								console.log("Zoom: " + light.shadowInfo.camera.zoom);
							}
							
							if (light.shadowInfo.camera.fov !== undefined) {
								console.log("FOV: " + light.shadowInfo.camera.fov + "°");
								console.log("Aspect: " + light.shadowInfo.camera.aspect);
							}
							console.groupEnd();	// shadow camera group
						}
					}
				} else {
					console.log("Enabled: false");
				}
				console.groupEnd(); // Shadow settings group
			}

			printOrbitControlsDetails(controls) {
				console.log("Enabled: " + controls.enabled);
				console.log("Target: [" + controls.target.join(", ") + "]");
				console.log("Distance limits: " + controls.minDistance + " - " + controls.maxDistance);
				console.log("Polar angle limits: " + 
					(controls.minPolarAngle * 180 / Math.PI).toFixed(2) + "° - " + 
					(controls.maxPolarAngle * 180 / Math.PI).toFixed(2) + "°");
				console.log("Azimuth angle limits: " + 
					(controls.minAzimuthAngle * 180 / Math.PI).toFixed(2) + "° - " + 
					(controls.maxAzimuthAngle * 180 / Math.PI).toFixed(2) + "°");
				
				console.groupCollapsed("Interaction settings:");
				console.log("  Damping: " + controls.enableDamping + " (factor: " + controls.dampingFactor + ")");
				console.log("  Zoom: " + controls.enableZoom + " (speed: " + controls.zoomSpeed + ")");
				console.log("  Rotate: " + controls.enableRotate + " (speed: " + controls.rotateSpeed + ")");
				console.log("  Pan: " + controls.enablePan + " (speed: " + controls.panSpeed + ")");
				console.log("  Screen space panning: " + controls.screenSpacePanning);
				
				if (controls.autoRotate) {
					console.log("  Auto-rotate: " + controls.autoRotate + " (speed: " + controls.autoRotateSpeed + ")");
				}
				
				console.groupEnd();	// interaction settings group
			}

			printCameraDetails(cam, isActive) {
				if (isActive) {
					console.log("*** ACTIVE CAMERA ***");
				}
				
				console.log("Name: " + cam.name);
				console.log("UUID: " + cam.uuid);
				console.log("Category: " + cam.category);
				console.log("Camera type: " + cam.cameraType);
				console.log("Projection: " + cam.projectionType);
				console.log("Visible: " + cam.visible);
				console.log("Matrix auto-update: " + cam.matrixAutoUpdate);
				console.log("Layer mask: " + cam.layers);
				
				// 位置和旋转
				console.log("Position: [" + cam.position.join(", ") + "]");
				console.log("Rotation: [" + cam.rotation.join(", ") + "]°");
				if (cam.quaternion) {
					console.log("Quaternion: [" + cam.quaternion.join(", ") + "]");
				}
				
				// 投影参数
				console.groupCollapsed("Projection parameters:");
				console.log("Near: " + cam.near);
				console.log("Far: " + cam.far);
				console.log("Zoom: " + cam.zoom);
				
				if (cam.projectionType === 'perspective' && cam.perspective) {
					console.log("FOV: " + cam.perspective.fov + "°");
					console.log("Aspect ratio: " + cam.perspective.aspect.toFixed(4));
					console.log("Film gauge: " + cam.perspective.filmGauge + "mm");
					console.log("Film offset: " + cam.perspective.filmOffset);
				} else if (cam.projectionType === 'orthographic' && cam.orthographic) {
					console.log("Left: " + cam.orthographic.left);
					console.log("Right: " + cam.orthographic.right);
					console.log("Top: " + cam.orthographic.top);
					console.log("Bottom: " + cam.orthographic.bottom);
					
					if (cam.orthographic.view.enabled) {
						console.log("Viewport: " + 
							cam.orthographic.view.width + "x" + cam.orthographic.view.height + 
							" at (" + cam.orthographic.view.offsetX + ", " + cam.orthographic.view.offsetY + ")" +
							" of " + cam.orthographic.view.fullWidth + "x" + cam.orthographic.view.fullHeight);
					}
				}
				console.groupEnd();
				
				// 用户数据 - 修复循环引用问题
				if (cam.userData && Object.keys(cam.userData).length > 0) {
					console.groupCollapsed("User data:");
					
					if (cam.controlsTarget) {
						console.log("Controls target: [" + cam.controlsTarget.join(", ") + "]");
					}
					
					if (cam.rollAngle !== undefined) {
						console.log("Roll angle: " + cam.rollAngle + "°");
					}
					
					if (cam.upVector) {
						console.log("Up vector: [" + cam.upVector.join(", ") + "]");
					}
					
					// 排除已经显示的属性
					const excludeKeys = ['controlsTarget', 'rollAngle', 'upVector', 'keyframes', 'animationKeyframes'];
					
					// 使用安全的 JSON.stringify 方法处理循环引用
					const safeStringify = (obj, space = 2) => {
						const seen = new WeakSet();
						return JSON.stringify(obj, (key, value) => {
							// 处理循环引用
							if (typeof value === 'object' && value !== null) {
								if (seen.has(value)) {
									return '[Circular Reference]';
								}
								seen.add(value);
							}
							
							// 处理 THREE.js 特定对象
							if (value && value.isEuler) {
								return {
									type: 'Euler',
									_x: value._x,
									_y: value._y,
									_z: value._z,
									_order: value._order
								};
							}
							
							if (value && value.isVector3) {
								return {
									type: 'Vector3',
									x: value.x,
									y: value.y,
									z: value.z
								};
							}
							
							if (value && value.isQuaternion) {
								return {
									type: 'Quaternion',
									x: value.x,
									y: value.y,
									z: value.z,
									w: value.w
								};
							}
							
							if (value && value.isMatrix4) {
								return {
									type: 'Matrix4',
									elements: value.elements
								};
							}
							
							return value;
						}, space);
					};
					
					for (const key in cam.userData) {
						if (!excludeKeys.includes(key)) {
							const value = cam.userData[key];
							
							// 特殊处理 THREE.js 对象
							if (value && (value.isEuler || value.isVector3 || value.isQuaternion || value.isMatrix4)) {
								console.groupCollapsed(key + ":");
								
								if (value.isEuler) {
									console.log("Type: Euler");
									console.log("X: " + value._x + ", Y: " + value._y + ", Z: " + value._z);
									console.log("Order: " + value._order);
								} else if (value.isVector3) {
									console.log("Type: Vector3");
									console.log("X: " + value.x + ", Y: " + value.y + ", Z: " + value.z);
								} else if (value.isQuaternion) {
									console.log("Type: Quaternion");
									console.log("X: " + value.x + ", Y: " + value.y + ", Z: " + value.z + ", W: " + value.w);
								} else if (value.isMatrix4) {
									console.log("Type: Matrix4");
									console.log("Elements:");
									for (let i = 0; i < 4; i++) {
										console.log("  " + value.elements[i*4].toFixed(4) + " " + value.elements[i*4+1].toFixed(4) + " " + value.elements[i*4+2].toFixed(4) + " " + value.elements[i*4+3].toFixed(4));
									}
								}
								
								console.groupEnd();
							} else if (typeof value === 'object' && value !== null) {
								try {
									console.log(key + ": " + safeStringify(value));
								} catch (error) {
									console.log(key + ": [Object - cannot stringify due to circular structure]");
									console.groupCollapsed("View object details:");
									console.dir(value);
									console.groupEnd();
								}
							} else {
								console.log(key + ": " + value);
							}
						}
					}
					console.groupEnd();
				}
				
				// 动画信息
				if (cam.hasAnimation) {
					console.groupCollapsed("Animation info:");
					console.log("Keyframes: " + cam.keyframeCount);
					console.log("Duration: " + cam.animationInfo.duration.toFixed(2) + "s");
					console.log("Animates position: " + cam.animationInfo.hasPositionAnimation);
					console.log("Animates rotation: " + cam.animationInfo.hasRotationAnimation);
					console.log("Animates FOV: " + cam.animationInfo.hasFovAnimation);
					console.log("Animates roll: " + cam.animationInfo.hasRollAnimation);
					
					if (cam.animationInfo.frames.length > 0) {
						console.log("Frame range: " + Math.min(...cam.animationInfo.frames) + 
								   " - " + Math.max(...cam.animationInfo.frames));
					}
					console.groupEnd();
				}
				
				// 矩阵信息
				console.groupCollapsed("Matrix info:");
				console.log("Projection matrix determinant: " + cam.projectionMatrix.determinant);
				console.log("World matrix determinant: " + cam.matrixWorld.determinant);
				console.groupEnd();
			}

			printAnimationClipDetails(clip) {
				console.log("UUID: " + clip.uuid);
				console.log("Duration: " + clip.duration.toFixed(2) + "s (" + clip.frameCount + " frames)");
				console.log("Tracks: " + clip.tracks);
				console.log("Keyframes: " + clip.totalKeyframes);
				console.log("Loop mode: " + clip.loopMode);
				console.log("Blend mode: " + clip.blendMode);
				
				// 动画属性
				console.groupCollapsed("Animated properties:");
				for (const prop in clip.properties) {
					if (clip.properties[prop]) {
						console.log(prop + ": Yes");
					}
				}
				console.groupEnd();
				
				// 轨道分析
				if (clip.trackAnalysis) {
					console.groupCollapsed("Track analysis:");
					console.log("Object references: " + clip.trackAnalysis.objectReferences.size);
					
					console.log("Property types:");
					for (const propType in clip.trackAnalysis.propertyTypes) {
						if (clip.trackAnalysis.propertyTypes[propType] > 0) {
							console.log("  " + propType + ": " + clip.trackAnalysis.propertyTypes[propType]);
						}
					}
					
					console.log("Interpolation types:");
					for (const interpType in clip.trackAnalysis.interpolationTypes) {
						if (clip.trackAnalysis.interpolationTypes[interpType] > 0) {
							console.log("  " + interpType + ": " + clip.trackAnalysis.interpolationTypes[interpType]);
						}
					}
					
					console.log("Keyframe density: " + clip.trackAnalysis.keyframeDensity.averagePerSecond.toFixed(1) + " per second");
					console.groupEnd();
				}
				
				// 被动画控制的对象
				if (clip.animatedObjects && clip.animatedObjects.length > 0) {
					console.groupCollapsed("Animated objects (" + clip.animatedObjects.length + "):");
					clip.animatedObjects.forEach(objPath => {
						console.log("  " + objPath);
					});
					console.groupEnd();
				}
				
				// 动作状态
				if (clip.actionInfo) {
					console.groupCollapsed("Action state:");
					console.log("Is playing: " + clip.actionInfo.isPlaying);
					console.log("Is scheduled: " + clip.actionInfo.isScheduled);
					console.log("Time: " + clip.actionInfo.time.toFixed(2));
					console.log("Time scale: " + clip.actionInfo.timeScale);
					console.log("Weight: " + clip.actionInfo.weight);
					console.log("Loop: " + clip.actionInfo.loop);
					console.log("Enabled: " + clip.actionInfo.enabled);
					console.groupEnd();
				}
				
				// 用户数据
				if (Object.keys(clip.userData).length > 0) {
					console.groupCollapsed("User data:");
					for (const key in clip.userData) {
						const value = clip.userData[key];
						if (typeof value === 'object') {
							console.log(key + ": " + JSON.stringify(value, null, 2));
						} else {
							console.log(key + ": " + value);
						}
					}
					console.groupEnd();
				}
			}

			printAnimatedObjectDetails(obj) {
				console.log("Path: " + obj.path);
				
				if (obj.object) {
					console.log("Type: " + obj.type);
					console.log("Visible: " + obj.visible);
				}
				
				console.log("Clips: " + obj.clipCount + " (" + obj.clips.join(', ') + ")");
				console.log("Tracks: " + obj.trackCount);
				console.log("Property types: " + obj.propertyTypes.join(', '));
			}

			collectObjectInfo() {
				const objectStats = {
					total: 0,
					types: {},
					visible: 0,
					groups: 0,
					meshes: 0,
					lines: 0,
					points: 0
				};
				
				const objects = {};
				const geometryInfo = {
					faces: 0,
					vertices: 0,
					triangles: 0,
					byObject: {}
				};
				
				let totalFaces = 0;
				let totalVertices = 0;
				let totalTriangles = 0;
				
				// 获取动画信息以检查物体是否有动画
				const animationInfo = this.collectAnimationInfo();
				const animatedObjectsMap = new Map();
				
				if (animationInfo.animatedObjects.length > 0) {
					animationInfo.animatedObjects.forEach(obj => {
						animatedObjectsMap.set(obj.path, obj);
					});
				}
				
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
					
					// 检查物体是否有动画
					let hasAnimation = false;
					let animationInfo = null;
					
					// 检查用户数据中的关键帧
					if (child.userData) {
						const keyframes = child.userData.keyframes || child.userData.animationKeyframes;
						if (keyframes && keyframes.length > 0) {
							hasAnimation = true;
							animationInfo = {
								keyframeCount: keyframes.length,
								duration: Math.max(...keyframes.map(kf => kf.frame || 0)) / this.state.playback.fps,
								hasPositionAnimation: keyframes.some(kf => kf.position),
								hasRotationAnimation: keyframes.some(kf => kf.rotation || kf.quaternion),
								hasScaleAnimation: keyframes.some(kf => kf.scale)
							};
						}
					}
					
					// 检查是否在动画剪辑中被引用
					if (!hasAnimation && animatedObjectsMap.has(child.name)) {
						hasAnimation = true;
						const animObj = animatedObjectsMap.get(child.name);
						animationInfo = {
							keyframeCount: animObj.trackCount,
							duration: 0, // 需要从剪辑中计算
							hasAnimation: true
						};
					}
					
					// 收集几何体信息 - 修复部分
					if (child.isMesh && child.geometry) {
						const geometry = child.geometry;
						
						// 计算面数和顶点数
						let faces = 0;
						let vertices = 0;
						let triangles = 0;
						
						if (geometry.isBufferGeometry) {
							// BufferGeometry
							if (geometry.attributes.position) {
								vertices = geometry.attributes.position.count;
							}
							
							// 计算三角形数
							if (geometry.index) {
								triangles = geometry.index.count / 3;
							} else {
								// 没有索引，假设为三角形列表
								triangles = vertices / 3;
							}
							
							faces = triangles; // 对于三角形网格，面数=三角形数
						} else if (geometry.isGeometry) {
							// Legacy Geometry
							faces = geometry.faces.length;
							vertices = geometry.vertices.length;
							triangles = faces; // Geometry使用三角面
						}
						
						// 更新总计数
						totalFaces += faces;
						totalVertices += vertices;
						totalTriangles += triangles;
						
						// 存储对象级别的几何体信息
						geometryInfo.byObject[child.name || "unnamed_" + objectStats.total] = {
							type: "Mesh",
							vertices: vertices,
							faces: faces,
							triangles: triangles,
							hasNormals: !!geometry.attributes.normal,
							hasUVs: !!geometry.attributes.uv,
							hasColors: !!geometry.attributes.color
						};
					} else if (child.isLine && child.geometry) {
						// 线对象
						const geometry = child.geometry;
						let vertices = 0;
						
						if (geometry.attributes.position) {
							vertices = geometry.attributes.position.count;
						}
						
						totalVertices += vertices;
						
						geometryInfo.byObject[child.name || "unnamed_" + objectStats.total] = {
							type: "Line",
							vertices: vertices,
							segments: Math.max(0, vertices - 1)
						};
					} else if (child.isPoints && child.geometry) {
						// 点对象
						const geometry = child.geometry;
						let vertices = 0;
						
						if (geometry.attributes.position) {
							vertices = geometry.attributes.position.count;
						}
						
						totalVertices += vertices;
						
						geometryInfo.byObject[child.name || "unnamed_" + objectStats.total] = {
							type: "Points",
							vertices: vertices
						};
					}
					
					// Store object information
					objects[child.name || "unnamed_" + objectStats.total] = {
						type: type,
						visible: child.visible,
						position: child.position ? child.position.toArray().map(function(v) { return v.toFixed(2); }) : null,
						userDataKeys: child.userData ? Object.keys(child.userData) : [],
						hasAnimation: hasAnimation,
						animationInfo: animationInfo
					};
				}.bind(this));
				
				// 更新几何体汇总信息
				geometryInfo.faces = totalFaces;
				geometryInfo.vertices = totalVertices;
				geometryInfo.triangles = totalTriangles;
				
				return {
					objectStats: objectStats,
					objects: objects,
					geometryInfo: geometryInfo
				};
			}

			collectMaterialAndTextureInfo() {
				const materialMap = new Map();
				const textureMap = new Map();
				
				this.scene.traverse(function(child) {
					// 收集材质和纹理
					if ((child.isMesh || child.isLine || child.isPoints) && child.material) {
						const materials = Array.isArray(child.material) ? child.material : [child.material];
						
						materials.forEach((material, index) => {
							if (material) {
								const materialId = material.uuid;
								const objectName = child.name || "unnamed_" + child.id;
								
								// 收集材质信息
								if (!materialMap.has(materialId)) {
									// 获取平面着色属性
									let flatShading = false;
									if (material.flatShading !== undefined) {
										flatShading = material.flatShading;
									} else if (material.shading !== undefined) {
										// 旧版本的Three.js使用shading属性
										flatShading = (material.shading === THREE.FlatShading);
									}
									
									const matInfo = {
										type: material.type || "Unknown",
										uuid: material.uuid,
										name: material.name || "Material_" + (materialMap.size + 1),
										objectCount: 0,
										objectNames: [], // 存储使用此材质的物体名称
										textureCount: 0,
										textures: {},
										properties: {
											// 基础属性
											color: material.color ? material.color.getHexString() : 'N/A',
											transparent: material.transparent || false,
											opacity: material.opacity || 1.0,
											side: material.side ? material.side.toString() : 'FrontSide',
											wireframe: material.wireframe || false,
											flatShading: flatShading,
											
											// PBR属性
											roughness: material.roughness !== undefined ? material.roughness : 1.0,
											metalness: material.metalness !== undefined ? material.metalness : 0.0,
											
											// 自发光属性
											emissive: material.emissive ? material.emissive.getHexString() : '000000',
											emissiveIntensity: material.emissiveIntensity !== undefined ? material.emissiveIntensity : 0.0,
											
											// 贴图强度属性
											bumpScale: material.bumpScale !== undefined ? material.bumpScale : 1.0,
											normalScale: material.normalScale ? {
												x: material.normalScale.x,
												y: material.normalScale.y
											} : { x: 1, y: 1 },
											displacementScale: material.displacementScale !== undefined ? material.displacementScale : 1.0,
											displacementBias: material.displacementBias !== undefined ? material.displacementBias : 0.0,
											aoMapIntensity: material.aoMapIntensity !== undefined ? material.aoMapIntensity : 1.0,
											
											// 其他材质属性
											specular: material.specular ? material.specular.getHexString() : 'N/A',
											shininess: material.shininess !== undefined ? material.shininess : 30.0,
											refractionRatio: material.refractionRatio !== undefined ? material.refractionRatio : 0.98,
											reflectivity: material.reflectivity !== undefined ? material.reflectivity : 1.0,
											
											// 透明属性
											alphaTest: material.alphaTest !== undefined ? material.alphaTest : 0.0,
											depthTest: material.depthTest !== undefined ? material.depthTest : true,
											depthWrite: material.depthWrite !== undefined ? material.depthWrite : true,
											polygonOffset: material.polygonOffset || false,
											polygonOffsetFactor: material.polygonOffsetFactor || 0,
											polygonOffsetUnits: material.polygonOffsetUnits || 0
										}
									};
									
									// 检查所有可能的纹理类型
									const textureTypes = [
										'map', 'normalMap', 'roughnessMap', 'metalnessMap',
										'emissiveMap', 'aoMap', 'specularMap', 'alphaMap',
										'bumpMap', 'displacementMap', 'lightMap', 'envMap'
									];
									
									textureTypes.forEach(texType => {
										if (material[texType] && material[texType].isTexture) {
											const texture = material[texType];
											
											// 统计材质使用了多少张不同的纹理
											matInfo.textureCount++;
											
											// 保存贴图的完整信息
											matInfo.textures[texType] = {
												uuid: texture.uuid,
												source: this.getTextureSourceInfo(texture),
												size: texture.image ? 
													texture.image.width + "x" + texture.image.height : 'Unknown',
												format: texture.format !== undefined ? texture.format.toString() : 'RGBA',
												// 针对特定贴图类型添加额外属性
												repeat: texture.repeat ? { 
													x: texture.repeat.x, 
													y: texture.repeat.y 
												} : { x: 1, y: 1 },
												offset: texture.offset ? { 
													x: texture.offset.x, 
													y: texture.offset.y 
												} : { x: 0, y: 0 },
												rotation: texture.rotation || 0,
												center: texture.center ? { 
													x: texture.center.x, 
													y: texture.center.y 
												} : { x: 0.5, y: 0.5 }
											};
											
											// 收集纹理信息（详细数据）
											const textureId = texture.uuid;
											
											if (!textureMap.has(textureId)) {
												// 首次遇到这个纹理
												textureMap.set(textureId, {
													uuid: texture.uuid,
													channels: [texType], // 记录使用这个纹理的所有通道
													source: this.getTextureSourceInfo(texture),
													size: texture.image ? 
														texture.image.width + "x" + texture.image.height : 'Unknown',
													format: texture.format !== undefined ? texture.format.toString() : 'RGBA',
													wrapS: texture.wrapS,
													wrapT: texture.wrapT,
													repeat: texture.repeat ? { 
														x: texture.repeat.x, 
														y: texture.repeat.y 
													} : { x: 1, y: 1 },
													offset: texture.offset ? { 
														x: texture.offset.x, 
														y: texture.offset.y 
													} : { x: 0, y: 0 },
													rotation: texture.rotation || 0,
													anisotropy: texture.anisotropy || 1,
													encoding: texture.encoding || 3000, // THREE.LinearEncoding
													usedByMaterials: [{
														materialId: materialId,
														channels: [texType]
													}]
												});
											} else {
												// 纹理已存在，更新信息
												const texInfo = textureMap.get(textureId);
												
												// 检查这个材质是否已经记录过
												const materialUsage = texInfo.usedByMaterials.find(usage => 
													usage.materialId === materialId
												);
												
												if (materialUsage) {
													// 材质已记录，添加新的通道
													if (!materialUsage.channels.includes(texType)) {
														materialUsage.channels.push(texType);
													}
												} else {
													// 材质未记录，添加新的材质使用记录
													texInfo.usedByMaterials.push({
														materialId: materialId,
														channels: [texType]
													});
												}
												
												// 添加通道到纹理的通道列表
												if (!texInfo.channels.includes(texType)) {
													texInfo.channels.push(texType);
												}
											}
										}
									});
									
									materialMap.set(materialId, matInfo);
								}
								
								// 更新材质使用计数和物体名称列表
								const matInfo = materialMap.get(materialId);
								matInfo.objectCount++;
								
								// 添加物体名称到列表（去重）
								if (!matInfo.objectNames.includes(objectName)) {
									matInfo.objectNames.push(objectName);
								}
							}
						});
					}
				}.bind(this));
				
				// 将Map转换为普通对象以便返回
				const materials = {};
				const textures = {};
				
				materialMap.forEach((value, key) => {
					materials[key] = value;
				});
				
				textureMap.forEach((value, key) => {
					textures[key] = value;
				});
				
				return {
					materialMap: materialMap,
					textureMap: textureMap,
					materials: materials,
					textures: textures
				};
			}

			calculateMaterialSummary(materials, textures) {
				const summary = {
					totalMaterials: Object.keys(materials).length,
					totalTextures: Object.keys(textures).length,
					materialsByType: {},
					texturesByType: {},
					textureReuseStats: {
						uniqueTextures: Object.keys(textures).length,
						totalTextureReferences: 0,
						averageReuse: 0
					},
					materialStats: {
						withFlatShading: 0,
						withTransparency: 0,
						withWireframe: 0,
						withBumpMapping: 0,
						withNormalMapping: 0,
						withDisplacement: 0
					}
				};
				
				// 统计材质信息
				Object.values(materials).forEach(matInfo => {
					const type = matInfo.type;
					summary.materialsByType[type] = (summary.materialsByType[type] || 0) + 1;
					
					// 统计材质属性
					if (matInfo.properties.flatShading) {
						summary.materialStats.withFlatShading++;
					}
					if (matInfo.properties.transparent) {
						summary.materialStats.withTransparency++;
					}
					if (matInfo.properties.wireframe) {
						summary.materialStats.withWireframe++;
					}
					
					// 检查是否有特定贴图
					if (matInfo.textures.bumpMap) {
						summary.materialStats.withBumpMapping++;
					}
					if (matInfo.textures.normalMap) {
						summary.materialStats.withNormalMapping++;
					}
					if (matInfo.textures.displacementMap) {
						summary.materialStats.withDisplacement++;
					}
					
					// 统计纹理引用次数
					summary.textureReuseStats.totalTextureReferences += Object.keys(matInfo.textures).length;
				});
				
				// 计算纹理复用统计
				if (summary.textureReuseStats.uniqueTextures > 0) {
					summary.textureReuseStats.averageReuse = 
						(summary.textureReuseStats.totalTextureReferences / summary.textureReuseStats.uniqueTextures).toFixed(2);
				}
				
				// 按通道类型统计纹理
				Object.values(textures).forEach(texInfo => {
					texInfo.channels.forEach(channel => {
						summary.texturesByType[channel] = (summary.texturesByType[channel] || 0) + 1;
					});
				});
				
				return summary;
			}

			getTextureSourceInfo(texture) {
				if (!texture || !texture.isTexture) return "No texture";
				
				if (!texture.image) {
					return "No image data";
				}
				
				if (texture.image.src) {
					const src = texture.image.src;
					if (src.startsWith('blob:')) {
						return "Blob URL: " + src.substring(0, 30) + "...";
					} else if (src.startsWith('data:')) {
						return "Data URL: " + src.substring(0, 30) + "...";
					} else {
						return "URL: " + (src.length > 50 ? src.substring(0, 50) + "..." : src);
					}
				} else if (texture.image.data) {
					return "ImageData: " + texture.image.width + "x" + texture.image.height;
				} else if (texture.image.canvas) {
					return "Canvas";
				} else if (texture.image.video) {
					return "Video";
				} else if (texture.image instanceof ImageBitmap) {
					return "ImageBitmap: " + texture.image.width + "x" + texture.image.height;
				}
				
				return "Unknown source type";
			}

			getTextureEncodingName(encoding) {
				if (encoding === undefined || encoding === null) return "Unknown";
				
				// Three.js 中的编码常量
				const encodingNames = {
					3000: "Linear",
					3001: "sRGB",
					3002: "Gamma",
					3003: "RGBE",
					3004: "LogLuv",
					3005: "RGBM7",
					3006: "RGBM16",
					3007: "RGBD",
					3008: "BasicDepth",
					3009: "RGBA"
				};
				
				return encodingNames[encoding] || "Unknown (" + encoding + ")";
			}

			collectLightInfo() {
				const lightInfo = {
					totalLights: 0,
					lightsByType: {},
					lights: [],
					shadowEnabledLights: 0,
					shadowSettings: {
						enabled: this.state.lights ? this.state.lights.shadowsEnabled : false,
						shadowMapType: this.renderer.shadowMap ? this.renderer.shadowMap.type : 0,
						shadowMapAutoUpdate: this.renderer.shadowMap ? this.renderer.shadowMap.autoUpdate : true,
						shadowMapNeedsUpdate: this.renderer.shadowMap ? this.renderer.shadowMap.needsUpdate : false
					}
				};
				
				// 获取动画信息以检查灯光是否有动画
				const animationInfo = this.collectAnimationInfo();
				const animatedObjectsMap = new Map();
				
				if (animationInfo.animatedObjects.length > 0) {
					animationInfo.animatedObjects.forEach(obj => {
						animatedObjectsMap.set(obj.path, obj);
					});
				}
				
				// 收集所有灯光
				const allLights = [];
				this.scene.traverse(child => {
					if (child.isLight) {
						allLights.push(child);
					}
				});
				
				lightInfo.totalLights = allLights.length;
				
				// 分析每个灯光
				allLights.forEach((light, index) => {
					// 检查灯光是否有动画
					let hasAnimation = false;
					let animationInfo = null;
					
					// 检查用户数据中的关键帧
					if (light.userData) {
						const keyframes = light.userData.keyframes || light.userData.animationKeyframes;
						if (keyframes && keyframes.length > 0) {
							hasAnimation = true;
							animationInfo = {
								keyframeCount: keyframes.length,
								duration: Math.max(...keyframes.map(kf => kf.frame || 0)) / (this.state.playback ? this.state.playback.fps : 30),
								hasPositionAnimation: keyframes.some(kf => kf.position),
								hasIntensityAnimation: keyframes.some(kf => kf.intensity !== undefined),
								hasColorAnimation: keyframes.some(kf => kf.color)
							};
						}
					}
					
					// 检查是否在动画剪辑中被引用
					if (!hasAnimation && animatedObjectsMap.has(light.name)) {
						hasAnimation = true;
						const animObj = animatedObjectsMap.get(light.name);
						animationInfo = {
							keyframeCount: animObj.trackCount,
							duration: 0,
							hasAnimation: true
						};
					}
					
					const lightData = {
						id: index + 1,
						name: light.name || "Light_" + (index + 1),
						type: light.type,
						uuid: light.uuid,
						position: light.position ? light.position.toArray().map(v => v.toFixed(2)) : [0, 0, 0],
						color: light.color ? light.color.getHexString() : 'ffffff',
						intensity: light.intensity || 1.0,
						visible: light.visible,
						castShadow: light.castShadow || false,
						hasAnimation: hasAnimation,
						animationInfo: animationInfo,
						shadowInfo: {
							enabled: false
						},
						specificProperties: {}
					};
					
					// 根据灯光类型收集特定属性
					switch (light.type) {
						case 'DirectionalLight':
							lightData.specificProperties = {
								target: light.target ? light.target.position.toArray().map(v => v.toFixed(2)) : [0, 0, 0]
							};
							break;
							
						case 'SpotLight':
							lightData.specificProperties = {
								angle: light.angle ? (light.angle * (180 / Math.PI)).toFixed(2) + '°' : '45°',
								penumbra: light.penumbra || 0.0,
								distance: light.distance || 0.0,
								decay: light.decay || 2.0,
								target: light.target ? light.target.position.toArray().map(v => v.toFixed(2)) : [0, 0, 0]
							};
							break;
							
						case 'PointLight':
							lightData.specificProperties = {
								distance: light.distance || 0.0,
								decay: light.decay || 2.0
							};
							break;
							
						case 'HemisphereLight':
							lightData.specificProperties = {
								groundColor: light.groundColor ? light.groundColor.getHexString() : 'ffffff'
							};
							break;
							
						case 'RectAreaLight':
							lightData.specificProperties = {
								width: light.width || 10,
								height: light.height || 10
							};
							break;
							
						case 'AmbientLight':
							// 环境光没有额外属性
							break;
					}
					
					// 收集阴影信息
					if (light.castShadow && light.shadow) {
						const shadow = light.shadow;
						const shadowCamera = shadow.camera;
						
						lightData.shadowInfo = {
							enabled: true,
							mapSize: {
								width: shadow.mapSize ? shadow.mapSize.width : 512,
								height: shadow.mapSize ? shadow.mapSize.height : 512
							},
							bias: shadow.bias || 0,
							normalBias: shadow.normalBias || 0,
							radius: shadow.radius || 1,
							blurSamples: shadow.blurSamples || 8,
							camera: {
								type: shadowCamera.type,
								near: shadowCamera.near || 0.1,
								far: shadowCamera.far || 1000
							}
						};
						
						// 根据相机类型收集特定参数
						if (shadowCamera.isOrthographicCamera) {
							lightData.shadowInfo.camera.left = shadowCamera.left || -5;
							lightData.shadowInfo.camera.right = shadowCamera.right || 5;
							lightData.shadowInfo.camera.top = shadowCamera.top || 5;
							lightData.shadowInfo.camera.bottom = shadowCamera.bottom || -5;
							lightData.shadowInfo.camera.zoom = shadowCamera.zoom || 1;
						} else if (shadowCamera.isPerspectiveCamera) {
							lightData.shadowInfo.camera.fov = shadowCamera.fov || 50;
							lightData.shadowInfo.camera.aspect = shadowCamera.aspect || 1;
						}
						
						lightInfo.shadowEnabledLights++;
					} else {
						// 确保shadowInfo有默认值
						lightData.shadowInfo = {
							enabled: false
						};
					}
					
					lightInfo.lights.push(lightData);
					
					// 统计灯光类型
					lightInfo.lightsByType[light.type] = (lightInfo.lightsByType[light.type] || 0) + 1;
				});
				
				return lightInfo;
			}

			getShadowMapTypeName(type) {
				const shadowTypes = {
					0: 'BasicShadowMap',
					1: 'PCFShadowMap',
					2: 'PCFSoftShadowMap',
					3: 'VSMShadowMap'
				};
				
				return shadowTypes[type] || "Unknown (" + type + ")";
			}

			collectCameraInfo() {
				const cameraInfo = {
					totalCameras: 0,
					camerasByType: {},
					cameras: [],
					activeCamera: null,
					defaultCameras: [],
					customCameras: [],
					sceneCameras: [],
					currentCameraType: this.state.cameras.currentType,
					orbitControlsInfo: null
				};
				
				// 收集所有默认相机
				cameraInfo.defaultCameras = this.state.cameras.default.map(camera => 
					this.analyzeCamera(camera, 'default')
				);
				
				// 收集所有自定义相机
				cameraInfo.customCameras = this.state.cameras.custom.map(camera => 
					this.analyzeCamera(camera, 'custom')
				);
				
				// 收集所有场景相机
				cameraInfo.sceneCameras = this.state.cameras.scene.map(camera => 
					this.analyzeCamera(camera, 'scene')
				);
				
				// 合并所有相机
				cameraInfo.cameras = [
					...cameraInfo.defaultCameras,
					...cameraInfo.customCameras,
					...cameraInfo.sceneCameras
				];
				
				cameraInfo.totalCameras = cameraInfo.cameras.length;
				
				// 统计相机类型分布
				cameraInfo.cameras.forEach(cam => {
					const cameraType = cam.cameraType || 'unknown';
					cameraInfo.camerasByType[cameraType] = (cameraInfo.camerasByType[cameraType] || 0) + 1;
					
					const projectionType = cam.projectionType;
					cameraInfo.camerasByType[projectionType] = (cameraInfo.camerasByType[projectionType] || 0) + 1;
				});
				
				// 当前激活相机
				if (this.camera) {
					cameraInfo.activeCamera = this.analyzeCamera(this.camera, 'active');
					cameraInfo.activeCamera.userData = this.camera.userData;
				}
				
				// OrbitControls信息
				if (this.controls) {
					cameraInfo.orbitControlsInfo = this.analyzeOrbitControls();
				}
				
				return cameraInfo;
			}

			analyzeCamera(camera, category) {
				const camInfo = {
					name: camera.name || "Unnamed_" + camera.uuid.substring(0, 8),
					uuid: camera.uuid,
					category: category,
					cameraType: camera.userData ? camera.userData.cameraType || 'free' : 'free',
					projectionType: camera.isPerspectiveCamera ? 'perspective' : 
								   camera.isOrthographicCamera ? 'orthographic' : 'unknown',
					position: camera.position.toArray().map(v => v.toFixed(2)),
					rotation: camera.rotation.toArray().map(v => (v * 180 / Math.PI).toFixed(2)),
					quaternion: camera.quaternion ? camera.quaternion.toArray().map(v => v.toFixed(4)) : null,
					
					// 通用属性
					near: camera.near,
					far: camera.far,
					zoom: camera.zoom || 1,
					viewport: camera.viewport || { x: 0, y: 0, width: 1, height: 1 },
					layers: camera.layers.mask,
					visible: camera.visible,
					matrixAutoUpdate: camera.matrixAutoUpdate,
					
					// 投影特定属性
					perspective: null,
					orthographic: null,
					
					// 用户数据
					userData: camera.userData || {},
					
					// 动画信息
					hasAnimation: false,
					keyframeCount: 0,
					animationInfo: null
				};
				
				// 透视相机属性
				if (camera.isPerspectiveCamera) {
					camInfo.perspective = {
						fov: camera.fov,
						aspect: camera.aspect,
						filmGauge: camera.filmGauge || 35,
						filmOffset: camera.filmOffset || 0
					};
				}
				
				// 正交相机属性
				if (camera.isOrthographicCamera) {
					camInfo.orthographic = {
						left: camera.left,
						right: camera.right,
						top: camera.top,
						bottom: camera.bottom,
						view: {
							enabled: camera.view ? true : false,
							fullWidth: camera.view ? camera.view.fullWidth : 0,
							fullHeight: camera.view ? camera.view.fullHeight : 0,
							offsetX: camera.view ? camera.view.offsetX : 0,
							offsetY: camera.view ? camera.view.offsetY : 0,
							width: camera.view ? camera.view.width : 0,
							height: camera.view ? camera.view.height : 0
						}
					};
				}
				
				// 检查动画信息
				if (camera.userData) {
					// 检查关键帧
					const keyframes = camera.userData.keyframes || camera.userData.animationKeyframes;
					if (keyframes && keyframes.length > 0) {
						camInfo.hasAnimation = true;
						camInfo.keyframeCount = keyframes.length;
						camInfo.animationInfo = {
							frames: keyframes.map(kf => kf.frame || 0),
							duration: Math.max(...keyframes.map(kf => kf.frame || 0)) / this.state.playback.fps,
							hasPositionAnimation: keyframes.some(kf => kf.position),
							hasRotationAnimation: keyframes.some(kf => kf.rotation || kf.quaternion),
							hasFovAnimation: keyframes.some(kf => kf.fov !== undefined),
							hasRollAnimation: keyframes.some(kf => kf.roll !== undefined)
						};
					}
					
					// 检查控制目标
					if (camera.userData.controlsTarget) {
						camInfo.controlsTarget = camera.userData.controlsTarget.toArray().map(v => v.toFixed(2));
					}
					
					// 检查roll角度
					if (camera.userData.rollAngle !== undefined) {
						camInfo.rollAngle = camera.userData.rollAngle;
					}
					
					// 检查up向量
					if (camera.userData.upVector) {
						camInfo.upVector = camera.userData.upVector.toArray().map(v => v.toFixed(4));
					}
				}
				
				// 计算投影矩阵参数
				camInfo.projectionMatrix = {
					elements: camera.projectionMatrix.elements.map(v => v.toFixed(4)),
					determinant: camera.projectionMatrix.determinant().toFixed(4)
				};
				
				// 计算视图矩阵参数
				camera.updateMatrixWorld();
				camInfo.matrixWorld = {
					elements: camera.matrixWorld.elements.map(v => v.toFixed(4)),
					determinant: camera.matrixWorld.determinant().toFixed(4)
				};
				
				return camInfo;
			}

			analyzeOrbitControls() {
				if (!this.controls) return null;
				
				return {
					enabled: this.controls.enabled,
					target: this.controls.target.toArray().map(v => v.toFixed(2)),
					minDistance: this.controls.minDistance,
					maxDistance: this.controls.maxDistance,
					minPolarAngle: this.controls.minPolarAngle,
					maxPolarAngle: this.controls.maxPolarAngle,
					minAzimuthAngle: this.controls.minAzimuthAngle,
					maxAzimuthAngle: this.controls.maxAzimuthAngle,
					enableDamping: this.controls.enableDamping,
					dampingFactor: this.controls.dampingFactor,
					enableZoom: this.controls.enableZoom,
					zoomSpeed: this.controls.zoomSpeed,
					enableRotate: this.controls.enableRotate,
					rotateSpeed: this.controls.rotateSpeed,
					enablePan: this.controls.enablePan,
					panSpeed: this.controls.panSpeed,
					screenSpacePanning: this.controls.screenSpacePanning,
					keyPanSpeed: this.controls.keyPanSpeed,
					autoRotate: this.controls.autoRotate,
					autoRotateSpeed: this.controls.autoRotateSpeed,
					keys: this.controls.keys,
					mouseButtons: this.controls.mouseButtons,
					touches: this.controls.touches,
					cameraUp: this.controls.object ? this.controls.object.up.toArray().map(v => v.toFixed(4)) : null
				};
			}

			collectAnimationInfo() {
				const animationInfo = {
					hasAnimations: false,
					totalClips: 0,
					totalTracks: 0,
					totalKeyframes: 0,
					clips: [],
					animatedObjects: [],
					playbackInfo: {
						fps: this.state.playback.fps,
						totalFrames: this.state.playback.totalFrames,
						currentFrame: this.state.playback.currentFrame,
						isPlaying: this.state.playback.playing || false,
						loopMode: this.state.playback.loop || 'once',
						speed: this.state.playback.speed || 1.0,
						timeScale: this.state.animationMixer ? this.state.animationMixer.timeScale : 1.0
					},
					mixerInfo: null,
					clipStatistics: {
						byDuration: { short: 0, medium: 0, long: 0 },
						byTrackCount: { simple: 0, medium: 0, complex: 0 },
						byPropertyType: {
							position: 0,
							rotation: 0,
							scale: 0,
							morph: 0,
							visibility: 0,
							other: 0
						}
					},
					// 添加独立的统计信息，不依赖 mixerInfo
					statistics: {
						totalDuration: 0,
						averageDuration: 0,
						maxDuration: 0
					}
				};
				
				// 如果有动画混合器，收集混合器信息
				if (this.state.animationMixer) {
					animationInfo.mixerInfo = {
						time: this.state.animationMixer.time,
						timeScale: this.state.animationMixer.timeScale,
						activeActionsCount: 0,
						totalRoots: 0
					};
				}
				
				// 收集动画剪辑信息
				if (this.state.currentAnimations && this.state.currentAnimations.length > 0) {
					animationInfo.totalClips = this.state.currentAnimations.length;
					animationInfo.hasAnimations = true;
					
					let totalDuration = 0;
					let maxDuration = 0;
					
					this.state.currentAnimations.forEach((anim, index) => {
						// 分析动画轨道
						const trackAnalysis = this.analyzeAnimationTracks(anim.tracks);
						
						// 计算动画时长
						const duration = anim.duration;
						totalDuration += duration;
						maxDuration = Math.max(maxDuration, duration);
						
						// 检查动画是否循环
						const loopMode = this.getClipLoopMode(anim);
						
						// 创建动画剪辑信息
						const clipInfo = {
							id: index,
							name: anim.name || "Clip_" + index,
							uuid: anim.uuid || "clip_" + index,
							duration: duration,
							frameCount: Math.ceil(duration * this.state.playback.fps),
							tracks: anim.tracks.length,
							totalKeyframes: trackAnalysis.totalKeyframes,
							loopMode: loopMode,
							blendMode: this.getClipBlendMode(anim),
							trackAnalysis: trackAnalysis,
							animatedObjects: this.getAnimatedObjectsFromClip(anim),
							properties: {
								hasPositionAnimation: trackAnalysis.propertyTypes.position > 0,
								hasRotationAnimation: trackAnalysis.propertyTypes.rotation > 0,
								hasScaleAnimation: trackAnalysis.propertyTypes.scale > 0,
								hasMorphAnimation: trackAnalysis.propertyTypes.morph > 0,
								hasVisibilityAnimation: trackAnalysis.propertyTypes.visibility > 0,
								hasColorAnimation: trackAnalysis.propertyTypes.color > 0,
								hasOpacityAnimation: trackAnalysis.propertyTypes.opacity > 0,
								hasFOVAnimation: trackAnalysis.propertyTypes.fov > 0,
								hasIntensityAnimation: trackAnalysis.propertyTypes.intensity > 0
							},
							metadata: anim.metadata || {},
							userData: anim.userData || {}
						};
						
						// 添加当前播放状态（如果混合器中有对应动作）
						if (this.state.animationMixer) {
							const action = this.state.animationMixer.existingAction(anim);
							if (action) {
								clipInfo.actionInfo = {
									isPlaying: action.isRunning(),
									isScheduled: action.isScheduled(),
									time: action.time,
									timeScale: action.timeScale,
									weight: action.weight,
									loop: action.loop,
									enabled: action.enabled,
									clampWhenFinished: action.clampWhenFinished,
									zeroSlopeAtStart: action.zeroSlopeAtStart,
									zeroSlopeAtEnd: action.zeroSlopeAtEnd
								};
								
								if (action.isRunning()) {
									animationInfo.mixerInfo.activeActionsCount++;
								}
							}
						}
						
						animationInfo.clips.push(clipInfo);
						animationInfo.totalTracks += anim.tracks.length;
						animationInfo.totalKeyframes += trackAnalysis.totalKeyframes;
						
						// 更新统计信息
						this.updateClipStatistics(animationInfo.clipStatistics, clipInfo);
					});
					
					// 计算独立于 mixerInfo 的统计信息
					if (animationInfo.totalClips > 0) {
						animationInfo.statistics.totalDuration = totalDuration;
						animationInfo.statistics.averageDuration = totalDuration / animationInfo.totalClips;
						animationInfo.statistics.maxDuration = maxDuration;
						
						// 如果有 mixerInfo，也更新它
						if (animationInfo.mixerInfo) {
							animationInfo.mixerInfo.statistics = {
								totalDuration: totalDuration,
								averageDuration: totalDuration / animationInfo.totalClips,
								maxDuration: maxDuration
							};
						}
					}
					
					// 收集所有被动画控制的对象
					animationInfo.animatedObjects = this.collectAnimatedObjects();
				}
				
				// 如果有混合器，收集根对象信息
				if (this.state.animationMixer && this.state.animationMixer._roots) {
					animationInfo.mixerInfo.totalRoots = this.state.animationMixer._roots.length;
				}
				
				return animationInfo;
			}

			analyzeAnimationTracks(tracks) {
				const analysis = {
					totalKeyframes: 0,
					tracksByType: {},
					propertyTypes: {
						position: 0,
						rotation: 0,
						scale: 0,
						morph: 0,
						visibility: 0,
						color: 0,
						opacity: 0,
						fov: 0,
						intensity: 0,
						other: 0
					},
					interpolationTypes: {
						linear: 0,
						step: 0,
						cubic: 0,
						unknown: 0
					},
					keyframeDensity: {
						averagePerSecond: 0,
						maxPerTrack: 0,
						minPerTrack: Infinity
					},
					objectReferences: new Set()
				};
				
				let totalKeyframesAllTracks = 0;
				
				tracks.forEach(track => {
					// 计算关键帧数量
					const keyframeCount = track.times ? track.times.length : 0;
					totalKeyframesAllTracks += keyframeCount;
					
					// 统计轨道类型
					const trackType = track.constructor.name;
					analysis.tracksByType[trackType] = (analysis.tracksByType[trackType] || 0) + 1;
					
					// 分析属性类型
					const propertyType = this.getAnimationPropertyType(track.name);
					analysis.propertyTypes[propertyType] = (analysis.propertyTypes[propertyType] || 0) + 1;
					
					// 分析插值类型
					const interpolationType = track.getInterpolation ? track.getInterpolation() : 'unknown';
					analysis.interpolationTypes[interpolationType] = (analysis.interpolationTypes[interpolationType] || 0) + 1;
					
					// 更新关键帧密度
					if (keyframeCount > analysis.keyframeDensity.maxPerTrack) {
						analysis.keyframeDensity.maxPerTrack = keyframeCount;
					}
					if (keyframeCount < analysis.keyframeDensity.minPerTrack) {
						analysis.keyframeDensity.minPerTrack = keyframeCount;
					}
					
					// 提取对象引用
					const objectPath = this.extractObjectPathFromTrackName(track.name);
					if (objectPath) {
						analysis.objectReferences.add(objectPath);
					}
				});
				
				analysis.totalKeyframes = totalKeyframesAllTracks;
				
				// 计算平均关键帧密度（假设平均时长为5秒）
				const averageDuration = 5; // 默认值
				analysis.keyframeDensity.averagePerSecond = totalKeyframesAllTracks > 0 ? 
					(totalKeyframesAllTracks / tracks.length) / averageDuration : 0;
				
				if (analysis.keyframeDensity.minPerTrack === Infinity) {
					analysis.keyframeDensity.minPerTrack = 0;
				}
				
				return analysis;
			}

			getAnimationPropertyType(trackName) {
				const lowerName = trackName.toLowerCase();
				
				if (lowerName.includes('.position') || lowerName.includes('.position[')) {
					return 'position';
				} else if (lowerName.includes('.quaternion') || lowerName.includes('.rotation')) {
					return 'rotation';
				} else if (lowerName.includes('.scale')) {
					return 'scale';
				} else if (lowerName.includes('.morph') || lowerName.includes('.influences')) {
					return 'morph';
				} else if (lowerName.includes('.visible') || lowerName.includes('.visibility')) {
					return 'visibility';
				} else if (lowerName.includes('.color') || lowerName.includes('.emissive')) {
					return 'color';
				} else if (lowerName.includes('.opacity') || lowerName.includes('.transparent')) {
					return 'opacity';
				} else if (lowerName.includes('.fov') || lowerName.includes('.fieldofview')) {
					return 'fov';
				} else if (lowerName.includes('.intensity')) {
					return 'intensity';
				}
				
				return 'other';
			}

			extractObjectPathFromTrackName(trackName) {
				// 典型的轨道名称格式: "objectName.property" 或 "objectName.property[index]"
				const match = trackName.match(/^([^.]+)/);
				return match ? match[1] : null;
			}

			getAnimatedObjectsFromClip(clip) {
				const objects = new Set();
				
				clip.tracks.forEach(track => {
					const objectPath = this.extractObjectPathFromTrackName(track.name);
					if (objectPath) {
						objects.add(objectPath);
					}
				});
				
				return Array.from(objects);
			}

			collectAnimatedObjects() {
				const animatedObjects = [];
				const objectMap = new Map();
				
				if (this.state.currentAnimations && this.state.currentAnimations.length > 0) {
					this.state.currentAnimations.forEach((anim, clipIndex) => {
						anim.tracks.forEach(track => {
							const objectPath = this.extractObjectPathFromTrackName(track.name);
							if (objectPath && !objectMap.has(objectPath)) {
								// 在场景中查找对象
								const object = this.findObjectByPath(objectPath);
								
								const animatedObject = {
									path: objectPath,
									name: objectPath.split('/').pop(),
									object: object,
									clipCount: 1,
									trackCount: 1,
									propertyTypes: new Set([this.getAnimationPropertyType(track.name)]),
									clips: [clipIndex]
								};
								
								if (object) {
									animatedObject.type = object.type;
									animatedObject.visible = object.visible;
									animatedObject.isMesh = object.isMesh;
									animatedObject.isCamera = object.isCamera;
									animatedObject.isLight = object.isLight;
								}
								
								objectMap.set(objectPath, animatedObject);
								animatedObjects.push(animatedObject);
							} else if (objectMap.has(objectPath)) {
								// 更新现有对象信息
								const existingObject = objectMap.get(objectPath);
								existingObject.trackCount++;
								existingObject.propertyTypes.add(this.getAnimationPropertyType(track.name));
								if (!existingObject.clips.includes(clipIndex)) {
									existingObject.clips.push(clipIndex);
									existingObject.clipCount++;
								}
							}
						});
					});
				}
				
				// 转换Set为数组
				animatedObjects.forEach(obj => {
					obj.propertyTypes = Array.from(obj.propertyTypes);
				});
				
				return animatedObjects;
			}

			findObjectByPath(objectPath) {
				// 简单实现：通过名称查找（实际实现可能需要处理层级路径）
				const pathParts = objectPath.split('/');
				const objectName = pathParts[pathParts.length - 1];
				
				let foundObject = null;
				this.scene.traverse(child => {
					if (child.name === objectName) {
						foundObject = child;
					}
				});
				
				return foundObject;
			}

			getClipLoopMode(clip) {
				if (clip.loop !== undefined) {
					const loopModes = {
						2200: 'Once',
						2201: 'Repeat',
						2202: 'PingPong'
					};
					return loopModes[clip.loop] || "Unknown (" + clip.loop + ")";
				}
				
				// 检查用户数据
				if (clip.userData && clip.userData.loopMode) {
					return clip.userData.loopMode;
				}
				
				return 'Once'; // 默认值
			}

			getClipBlendMode(clip) {
				if (clip.blendMode !== undefined) {
					const blendModes = {
						0: 'Normal',
						1: 'Additive',
						2: 'Subtractive',
						3: 'Multiply',
						4: 'Custom'
					};
					return blendModes[clip.blendMode] || "Unknown (" + clip.blendMode + ")";
				}
				
				return 'Normal'; // 默认值
			}

			updateClipStatistics(statistics, clipInfo) {
				// 按时长分类
				if (clipInfo.duration < 2) {
					statistics.byDuration.short++;
				} else if (clipInfo.duration < 10) {
					statistics.byDuration.medium++;
				} else {
					statistics.byDuration.long++;
				}
				
				// 按轨道数量分类
				if (clipInfo.tracks < 5) {
					statistics.byTrackCount.simple++;
				} else if (clipInfo.tracks < 20) {
					statistics.byTrackCount.medium++;
				} else {
					statistics.byTrackCount.complex++;
				}
				
				// 按属性类型统计
				const trackAnalysis = clipInfo.trackAnalysis;
				if (trackAnalysis && trackAnalysis.propertyTypes) {
					for (const propType in trackAnalysis.propertyTypes) {
						if (trackAnalysis.propertyTypes[propType] > 0) {
							statistics.byPropertyType[propType] = 
								(statistics.byPropertyType[propType] || 0) + 1;
						}
					}
				}
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
