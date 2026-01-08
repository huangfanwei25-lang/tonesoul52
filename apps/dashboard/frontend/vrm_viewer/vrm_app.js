/**
 * ToneSoul VRM 角色互動應用 v2
 * Enhanced with Darlin-inspired features:
 * - Lip sync animation (SALSA-style)
 * - State machine for animations (Animancer-style)
 * - Service code tracking
 * - Emotion-driven expressions
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMUtils, VRMExpressionPresetName } from '@pixiv/three-vrm';

// ============================================
// 配置 (Darlin-style)
// ============================================
const CONFIG = {
    API_URL: 'http://localhost:8000',
    VRM_API_PATH: '/vrm',
    OLLAMA_URL: 'http://localhost:11434',
    OLLAMA_MODEL: 'gemma3:4b',  // 本地 Ollama 模型

    // 使用本地 VRM 模型 (Makise Kurisu)
    HISTORY_LIMIT: 8,
    PERSONA_ID: 'darlin',
    DEFAULT_VRM: './kurisu.vrm',

    // 動畫設定 (from Darlin gpuconfig patterns)
    BLINK_INTERVAL: 3000,
    IDLE_BREATH_SPEED: 0.5,
    LIP_SYNC_SPEED: 15,
    EMOTION_BLEND_SPEED: 3,

    // 手勢動畫設定
    GESTURE_SPEED: 4,          // 動作速度
    GESTURE_SMOOTHING: 0.15,   // 平滑度
};

// ============================================
// 服務代碼系統 (Darlin-style TS001-TS007)
// ============================================
const ServiceCode = {
    TS001: { name: 'Council', status: 'idle' },
    TS002: { name: 'Gate', status: 'idle' },
    TS003: { name: 'PersonaDim', status: 'idle' },
    TS004: { name: 'Memory', status: 'idle' },
    TS005: { name: 'YSTM', status: 'idle' },
    TS006: { name: 'Audit', status: 'idle' },
    TS007: { name: 'LLM', status: 'idle' },
};

function updateServiceStatus(code, status) {
    if (ServiceCode[code]) {
        ServiceCode[code].status = status;
        console.log(`[${code}] ${ServiceCode[code].name}: ${status}`);
    }
}

// ============================================
// 狀態機系統 (Animancer FSM style)
// ============================================
const CharacterState = {
    IDLE: 'idle',
    LISTENING: 'listening',
    THINKING: 'thinking',
    SPEAKING: 'speaking',
    HAPPY: 'happy',
    SAD: 'sad',
    SURPRISED: 'surprised',
};

let currentState = CharacterState.IDLE;
let targetEmotion = 'neutral';
let emotionBlend = 0;

function transitionTo(newState) {
    if (currentState !== newState) {
        console.log(`State: ${currentState} → ${newState}`);
        currentState = newState;

        // 根據狀態更新表情目標
        switch (newState) {
            case CharacterState.SPEAKING:
            case CharacterState.IDLE:
                targetEmotion = 'neutral';
                break;
            case CharacterState.HAPPY:
                targetEmotion = 'happy';
                break;
            case CharacterState.SAD:
                targetEmotion = 'sad';
                break;
            case CharacterState.SURPRISED:
                targetEmotion = 'surprised';
                break;
            case CharacterState.THINKING:
                targetEmotion = 'relaxed';
                break;
        }
    }
}

// ============================================
// 全域狀態
// ============================================
let scene, camera, renderer, controls;
let currentVRM = null;
let clock = new THREE.Clock();
let isLoading = true;
let vrmStatus = {
    loaded: false,
    lastLoadedAt: null,
    lastError: null,
    hasHumanoid: false,
    hasExpressionManager: false,
    expressionNames: [],
    modelName: null,
};
let expressionNameMap = new Map();

// 嘴型同步
let isSpeaking = false;
let lipSyncPhase = 0;
let speakingText = '';
let speakingIndex = 0;

// 頭部追蹤 (VRM LookAt)
let lookAtTarget = new THREE.Object3D();
lookAtTarget.position.set(0, 1.3, 2);
let mousePosition = { x: 0, y: 0 };
let isMouseTracking = true;

// ============================================
// 手勢動畫系統 (Gesture Library)
// ============================================
const GestureType = {
    NONE: 'none',
    NOD: 'nod',           // 點頭
    SHAKE: 'shake',       // 搖頭
    WAVE: 'wave',         // 揮手
    BOW: 'bow',           // 鞠躬
    SHRUG: 'shrug',       // 聳肩
    THINKING: 'thinking', // 思考（歪頭）
    HAPPY: 'happy',       // 開心跳動
};

// 手勢觸發關鍵字映射
const GestureTriggers = {
    [GestureType.NOD]: ['是的', '對', '沒錯', '確實', '同意', '好的', '了解', '明白', 'OK', 'yes'],
    [GestureType.SHAKE]: ['不', '沒有', '不是', '不行', '別', '才不是', '不對', 'no'],
    [GestureType.WAVE]: ['你好', '嗨', '再見', '掰掰', 'hello', 'hi', 'bye'],
    [GestureType.BOW]: ['抱歉', '對不起', '謝謝', '感謝', 'sorry', 'thanks'],
    [GestureType.SHRUG]: ['不知道', '也許', '可能', '大概', '隨便', '?'],
    [GestureType.THINKING]: ['嗯...', '讓我想想', '思考', '這個嘛'],
    [GestureType.HAPPY]: ['太棒了', '開心', '好玩', '有趣', '哈哈'],
};

// 當前手勢狀態
let currentGesture = GestureType.NONE;
let gestureProgress = 0;
let gestureQueue = [];

// 手勢動畫定義（骨骼旋轉）
const GestureAnimations = {
    [GestureType.NOD]: {
        duration: 0.6,
        keyframes: [
            { t: 0.0, head: { x: 0, y: 0, z: 0 } },
            { t: 0.2, head: { x: 0.2, y: 0, z: 0 } },  // 低頭
            { t: 0.4, head: { x: -0.1, y: 0, z: 0 } }, // 抬頭
            { t: 0.6, head: { x: 0, y: 0, z: 0 } },
        ]
    },
    [GestureType.SHAKE]: {
        duration: 0.8,
        keyframes: [
            { t: 0.0, head: { x: 0, y: 0, z: 0 } },
            { t: 0.2, head: { x: 0, y: 0.25, z: 0 } },  // 右轉
            { t: 0.4, head: { x: 0, y: -0.25, z: 0 } }, // 左轉
            { t: 0.6, head: { x: 0, y: 0.15, z: 0 } },  // 右轉
            { t: 0.8, head: { x: 0, y: 0, z: 0 } },
        ]
    },
    [GestureType.WAVE]: {
        duration: 1.2,
        keyframes: [
            { t: 0.0, rightArm: { x: 0, y: 0, z: 0 } },
            { t: 0.2, rightArm: { x: -1.2, y: 0.3, z: 0.5 } },   // 舉手
            { t: 0.4, rightArm: { x: -1.2, y: 0.3, z: -0.3 } },  // 揮左
            { t: 0.6, rightArm: { x: -1.2, y: 0.3, z: 0.5 } },   // 揮右
            { t: 0.8, rightArm: { x: -1.2, y: 0.3, z: -0.3 } },  // 揮左
            { t: 1.0, rightArm: { x: -1.2, y: 0.3, z: 0.5 } },   // 揮右
            { t: 1.2, rightArm: { x: 0, y: 0, z: 0 } },
        ]
    },
    [GestureType.BOW]: {
        duration: 1.0,
        keyframes: [
            { t: 0.0, spine: { x: 0, y: 0, z: 0 }, head: { x: 0, y: 0, z: 0 } },
            { t: 0.3, spine: { x: 0.3, y: 0, z: 0 }, head: { x: 0.2, y: 0, z: 0 } },  // 鞠躬
            { t: 0.7, spine: { x: 0.3, y: 0, z: 0 }, head: { x: 0.2, y: 0, z: 0 } },  // 停留
            { t: 1.0, spine: { x: 0, y: 0, z: 0 }, head: { x: 0, y: 0, z: 0 } },
        ]
    },
    [GestureType.SHRUG]: {
        duration: 0.8,
        keyframes: [
            { t: 0.0, leftShoulder: { y: 0 }, rightShoulder: { y: 0 }, head: { z: 0 } },
            { t: 0.3, leftShoulder: { y: 0.2 }, rightShoulder: { y: 0.2 }, head: { z: 0.1 } },  // 聳肩
            { t: 0.6, leftShoulder: { y: 0.2 }, rightShoulder: { y: 0.2 }, head: { z: 0.1 } },
            { t: 0.8, leftShoulder: { y: 0 }, rightShoulder: { y: 0 }, head: { z: 0 } },
        ]
    },
    [GestureType.THINKING]: {
        duration: 0.5,
        keyframes: [
            { t: 0.0, head: { x: 0, y: 0, z: 0 } },
            { t: 0.3, head: { x: 0.05, y: 0.1, z: 0.15 } },  // 歪頭思考
            { t: 0.5, head: { x: 0.05, y: 0.1, z: 0.15 } },  // 保持
        ]
    },
    [GestureType.HAPPY]: {
        duration: 0.6,
        keyframes: [
            { t: 0.0, offset: { y: 0 } },
            { t: 0.15, offset: { y: 0.03 } },   // 跳起
            { t: 0.3, offset: { y: 0 } },
            { t: 0.45, offset: { y: 0.02 } },   // 再跳
            { t: 0.6, offset: { y: 0 } },
        ]
    },
};

// ============================================
// 初始化
// ============================================
async function init() {
    setupScene();
    setupLights();
    setupControls();
    setupEventListeners();

    updateServiceStatus('TS007', 'connecting');

    await loadVRM(CONFIG.DEFAULT_VRM);

    animate();
    hideLoading();

    updateServiceStatus('TS007', 'ready');
}

function setupScene() {
    const canvas = document.getElementById('vrm-canvas');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    scene.add(lookAtTarget);

    camera = new THREE.PerspectiveCamera(
        30,
        canvas.clientWidth / canvas.clientHeight,
        0.1,
        100
    );
    camera.position.set(0, 1.3, 2.5);

    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;

    window.addEventListener('resize', onWindowResize);
}

function setupLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
    mainLight.position.set(2, 3, 2);
    scene.add(mainLight);

    const fillLight = new THREE.DirectionalLight(0x8888ff, 0.4);
    fillLight.position.set(-2, 2, 1);
    scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0xffffff, 0.3);
    backLight.position.set(0, 2, -2);
    scene.add(backLight);

    // 輪廓光 (NiloToon style rim light)
    const rimLight = new THREE.DirectionalLight(0xaaaaff, 0.5);
    rimLight.position.set(0, 1, -3);
    scene.add(rimLight);
}

function setupControls() {
    const canvas = document.getElementById('vrm-canvas');
    controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 1.0, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 1;
    controls.maxDistance = 5;
    controls.maxPolarAngle = Math.PI / 2;
    controls.update();
}

// ============================================
// VRM 載入
// ============================================
async function loadVRM(url) {
    return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        loader.register((parser) => new VRMLoaderPlugin(parser));

        loader.load(
            url,
            (gltf) => {
                const vrm = gltf.userData.vrm;

                if (currentVRM) {
                    scene.remove(currentVRM.scene);
                    VRMUtils.deepDispose(currentVRM.scene);
                }

                currentVRM = vrm;
                VRMUtils.rotateVRM0(vrm);
                scene.add(vrm.scene);
                if (vrm.lookAt) {
                    vrm.lookAt.target = lookAtTarget;
                }
                refreshVRMStatus(vrm, null);

                // 列出可用表情
                if (vrm.expressionManager) {
                    const names = listExpressionNames(vrm);
                    console.log('Available expressions:', names);
                }

                console.log('VRM loaded:', vrm);
                resolve(vrm);
            },
            (progress) => {
                const percent = (progress.loaded / progress.total * 100).toFixed(0);
                updateLoadingText(`載入中... ${percent}%`);
            },
            (error) => {
                console.error('VRM load error:', error);
                refreshVRMStatus(null, error);
                reject(error);
            }
        );
    });
}

function refreshVRMStatus(vrm, error) {
    const expressions = listExpressionNames(vrm);
    expressionNameMap = new Map(expressions.map(name => [name.toLowerCase(), name]));

    vrmStatus = {
        loaded: !!vrm,
        lastLoadedAt: vrm ? new Date().toISOString() : vrmStatus.lastLoadedAt,
        lastError: error ? String(error) : null,
        hasHumanoid: !!vrm?.humanoid,
        hasExpressionManager: !!vrm?.expressionManager,
        expressionNames: expressions,
        modelName: vrm?.meta?.title || vrm?.meta?.name || null,
    };
}

function listExpressionNames(vrm) {
    const manager = vrm?.expressionManager;
    if (!manager || !manager.expressions) return [];
    const expressions = manager.expressions;
    if (Array.isArray(expressions)) {
        return expressions.map(e => e.expressionName || e.name).filter(Boolean);
    }
    if (expressions instanceof Map) {
        return Array.from(expressions.keys());
    }
    if (typeof expressions === 'object') {
        return Object.keys(expressions);
    }
    return [];
}

function resolveExpressionName(name) {
    if (!name) return null;
    const aliases = {
        neutral: ['neutral', 'default'],
        happy: ['happy', 'joy', 'smile'],
        sad: ['sad', 'sorrow'],
        angry: ['angry'],
        surprised: ['surprised', 'surprise'],
        relaxed: ['relaxed', 'calm'],
    };
    const candidates = aliases[name] || [name];
    for (const candidate of candidates) {
        const mapped = expressionNameMap.get(candidate.toLowerCase());
        if (mapped) return mapped;
    }
    return name;
}

// ============================================
// 動畫迴圈
// ============================================
let animateDebugOnce = true;
function animate() {
    requestAnimationFrame(animate);

    const deltaTime = clock.getDelta();

    // DEBUG: 在 if 外面 log
    if (animateDebugOnce) {
        console.log('🎬 animate() called, currentVRM:', currentVRM ? 'LOADED' : 'NULL');
        animateDebugOnce = false;
    }

    if (currentVRM) {
        if (currentVRM.lookAt) {
            const target = currentVRM.lookAt.target;
            if (!target || typeof target.getWorldPosition !== 'function') {
                console.warn('Invalid VRM lookAt target, disabling lookAt.');
                currentVRM.lookAt = null;
            } else {
                currentVRM.lookAt.target = lookAtTarget;
            }
        }
        currentVRM.update(deltaTime);

        idleAnimation(deltaTime);
        autoBlinkAnimation();
        lipSyncAnimation(deltaTime);
        emotionBlendAnimation(deltaTime);
        lookAtAnimation(deltaTime);
        gestureAnimation(deltaTime);  // 手勢動畫
    }

    controls.update();
    renderer.render(scene, camera);
}

// 待機呼吸動畫
let breathPhase = 0;
function idleAnimation(deltaTime) {
    if (!currentVRM) return;

    breathPhase += deltaTime * CONFIG.IDLE_BREATH_SPEED;
    const breathOffset = Math.sin(breathPhase) * 0.005;
    currentVRM.scene.position.y = breathOffset;
}

// 自動眨眼
let lastBlinkTime = 0;
let isBlinking = false;
function autoBlinkAnimation() {
    if (!currentVRM || !currentVRM.expressionManager) return;

    const now = Date.now();

    if (!isBlinking && now - lastBlinkTime > CONFIG.BLINK_INTERVAL + Math.random() * 1000) {
        isBlinking = true;
        lastBlinkTime = now;

        currentVRM.expressionManager.setValue('blink', 1.0);

        setTimeout(() => {
            if (currentVRM?.expressionManager) {
                currentVRM.expressionManager.setValue('blink', 0);
            }
            isBlinking = false;
        }, 100);
    }
}

// ============================================
// 嘴型同步 (SALSA-style)
// ============================================
function lipSyncAnimation(deltaTime) {
    if (!currentVRM?.expressionManager) return;

    if (isSpeaking) {
        lipSyncPhase += deltaTime * CONFIG.LIP_SYNC_SPEED;

        // 模擬嘴巴開合 (基於文字進度)
        const openAmount = Math.abs(Math.sin(lipSyncPhase)) * 0.8;

        // 設置嘴巴開合
        try {
            currentVRM.expressionManager.setValue('aa', openAmount);
        } catch (e) {
            // 備選: 使用其他嘴型
            try {
                currentVRM.expressionManager.setValue('a', openAmount);
            } catch (e2) { }
        }

        // 進度更新
        speakingIndex++;
        if (speakingIndex >= speakingText.length * 3) {
            stopSpeaking();
        }
    } else {
        // 嘴巴閉合
        try {
            currentVRM.expressionManager.setValue('aa', 0);
            currentVRM.expressionManager.setValue('a', 0);
        } catch (e) { }
    }
}

function startSpeaking(text) {
    speakingText = text;
    speakingIndex = 0;
    isSpeaking = true;
    lipSyncPhase = 0;
    transitionTo(CharacterState.SPEAKING);
}

function stopSpeaking() {
    isSpeaking = false;
    transitionTo(CharacterState.IDLE);
}

// ============================================
// 表情混合動畫 (Smooth transitions)
// ============================================
const emotionValues = {
    neutral: 0,
    happy: 0,
    sad: 0,
    angry: 0,
    surprised: 0,
    relaxed: 0,
};

function emotionBlendAnimation(deltaTime) {
    if (!currentVRM?.expressionManager) return;

    const blendSpeed = CONFIG.EMOTION_BLEND_SPEED * deltaTime;

    // 平滑過渡到目標表情
    Object.keys(emotionValues).forEach(emotion => {
        const targetValue = emotion === targetEmotion ? 1.0 : 0.0;
        emotionValues[emotion] += (targetValue - emotionValues[emotion]) * blendSpeed;

        // 應用表情
        try {
            const resolved = resolveExpressionName(emotion);
            if (resolved) {
                currentVRM.expressionManager.setValue(resolved, emotionValues[emotion]);
            }
        } catch (e) { }
    });
}

function setExpression(exprName) {
    targetEmotion = exprName;
    const resolved = resolveExpressionName(exprName);
    console.log('Expression target:', exprName);
    if (resolved && resolved !== exprName) {
        console.log('Expression resolved:', resolved);
    }
}

// ============================================
// 頭部追蹤 (VRM LookAt)
// ============================================
function lookAtAnimation(deltaTime) {
    if (!currentVRM || !isMouseTracking) return;

    // 計算目標位置 (基於滑鼠位置)
    const targetX = (mousePosition.x - 0.5) * 2;  // -1 到 1
    const targetY = (0.5 - mousePosition.y) * 1;  // 反轉 Y

    // 平滑更新目標
    lookAtTarget.position.x += (targetX - lookAtTarget.position.x) * deltaTime * 3;
    lookAtTarget.position.y += (1.3 + targetY * 0.3 - lookAtTarget.position.y) * deltaTime * 3;
    lookAtTarget.position.z = 2;
    lookAtTarget.updateMatrixWorld();

    // 使用 VRM LookAt 功能
    if (currentVRM.lookAt) {
        currentVRM.lookAt.target = lookAtTarget;
    } else {
        // 備援：手動旋轉頭部骨骼
        try {
            const head = currentVRM.humanoid?.getNormalizedBoneNode('head');
            if (head) {
                const targetRotY = targetX * 0.3;  // 左右旋轉
                const targetRotX = targetY * 0.2;  // 上下旋轉

                head.rotation.y += (targetRotY - head.rotation.y) * deltaTime * 5;
                head.rotation.x += (targetRotX - head.rotation.x) * deltaTime * 5;
            }
        } catch (e) { }
    }
}

function toggleMouseTracking(enabled) {
    isMouseTracking = enabled;
    console.log('Mouse tracking:', enabled ? 'ON' : 'OFF');
}

// ============================================
// 手勢動畫執行 (Gesture Animation Engine)
// ============================================
let gestureStartTime = 0;
let gestureBaseRotations = {};

function playGesture(gestureType) {
    if (!GestureAnimations[gestureType]) {
        console.warn('Unknown gesture:', gestureType);
        return;
    }

    currentGesture = gestureType;
    gestureProgress = 0;
    gestureStartTime = performance.now() / 1000;

    // 保存初始骨骼旋轉
    gestureBaseRotations = {};

    console.log('🎭 Playing gesture:', gestureType);
}

let gestureDebugOnce = true;
function gestureAnimation(deltaTime) {
    // Debug: log when gesture is active
    if (currentGesture !== GestureType.NONE && gestureDebugOnce) {
        console.log('🔄 gestureAnimation: currentGesture=', currentGesture, 'currentVRM=', !!currentVRM);
        gestureDebugOnce = false;
    }

    if (!currentVRM || currentGesture === GestureType.NONE) return;

    const anim = GestureAnimations[currentGesture];
    if (!anim) {
        console.warn('⚠️ Animation not found for:', currentGesture);
        return;
    }

    gestureProgress += deltaTime * CONFIG.GESTURE_SPEED;
    const t = Math.min(gestureProgress, anim.duration);

    // 找到當前關鍵幀
    const keyframes = anim.keyframes;
    let prevFrame = keyframes[0];
    let nextFrame = keyframes[keyframes.length - 1];

    for (let i = 0; i < keyframes.length - 1; i++) {
        if (t >= keyframes[i].t && t <= keyframes[i + 1].t) {
            prevFrame = keyframes[i];
            nextFrame = keyframes[i + 1];
            break;
        }
    }

    // 插值計算
    const frameDuration = nextFrame.t - prevFrame.t;
    const frameProgress = frameDuration > 0 ? (t - prevFrame.t) / frameDuration : 1;
    const smoothProgress = smoothstep(frameProgress);

    // 應用骨骼旋轉
    applyGestureFrame(prevFrame, nextFrame, smoothProgress);

    // 動畫結束
    if (gestureProgress >= anim.duration) {
        currentGesture = GestureType.NONE;
        console.log('🎭 Gesture complete');
    }
}

function smoothstep(t) {
    return t * t * (3 - 2 * t);
}

function applyGestureFrame(prevFrame, nextFrame, progress) {
    if (!currentVRM?.humanoid) {
        console.warn('⚠️ applyGestureFrame: No VRM humanoid!');
        return;
    }

    // 完整的骨骼映射 (動畫鍵名 → VRM 正規化骨骼名)
    const boneMap = {
        head: 'head',
        spine: 'spine',
        rightArm: 'rightUpperArm',
        leftArm: 'leftUpperArm',
        rightUpperArm: 'rightUpperArm',
        leftUpperArm: 'leftUpperArm',
        rightLowerArm: 'rightLowerArm',
        leftLowerArm: 'leftLowerArm',
        leftShoulder: 'leftShoulder',
        rightShoulder: 'rightShoulder',
        hips: 'hips',
        chest: 'chest',
        neck: 'neck',
    };

    // 處理每個骨骼 - 從 frame 裡取得所有骨骼鍵
    const allBones = new Set([
        ...Object.keys(prevFrame).filter(k => k !== 't' && k !== 'offset'),
        ...Object.keys(nextFrame).filter(k => k !== 't' && k !== 'offset')
    ]);

    allBones.forEach(boneName => {
        const vrmBoneName = boneMap[boneName];
        if (!vrmBoneName) {
            console.warn('⚠️ Unknown bone:', boneName);
            return;
        }

        try {
            const bone = currentVRM.humanoid.getNormalizedBoneNode(vrmBoneName);
            if (!bone) {
                console.warn('⚠️ Bone not found in VRM:', vrmBoneName);
                return;
            }

            const prev = prevFrame[boneName] || { x: 0, y: 0, z: 0 };
            const next = nextFrame[boneName] || { x: 0, y: 0, z: 0 };

            // 線性插值
            if (prev.x !== undefined) bone.rotation.x = lerp(prev.x, next.x, progress);
            if (prev.y !== undefined) bone.rotation.y = lerp(prev.y, next.y, progress);
            if (prev.z !== undefined) bone.rotation.z = lerp(prev.z, next.z, progress);
        } catch (e) {
            console.error('❌ Bone animation error:', boneName, e);
        }
    });

    // 處理位移（如開心跳動）
    if (prevFrame.offset || nextFrame.offset) {
        const prevY = prevFrame.offset?.y || 0;
        const nextY = nextFrame.offset?.y || 0;
        // 位移會加到呼吸動畫上
        const extraOffset = lerp(prevY, nextY, progress);
        currentVRM.scene.position.y += extraOffset;
    }
}

function lerp(a, b, t) {
    return a + (b - a) * t;
}

// ============================================
// AI 動作指令解析器
// ============================================
function detectGestureFromText(text) {
    for (const [gesture, triggers] of Object.entries(GestureTriggers)) {
        for (const keyword of triggers) {
            if (text.includes(keyword)) {
                return gesture;
            }
        }
    }
    return null;
}

// AI 可以直接發送的動作指令格式: [ACTION:nod] [ACTION:wave]
function parseActionCommands(text) {
    const actionRegex = /\[ACTION:(\w+)\]/gi;
    const matches = [...text.matchAll(actionRegex)];

    return matches.map(match => match[1].toLowerCase());
}

// 執行 AI 發送的動作指令
function executeAIActions(text) {
    // 0. 先檢查是否有新的手勢定義
    parseAndRegisterNewGestures(text);

    // 1. 先檢查明確的動作指令
    const explicitActions = parseActionCommands(text);
    if (explicitActions.length > 0) {
        explicitActions.forEach(action => {
            if (GestureType[action.toUpperCase()] || GestureAnimations[action]) {
                playGesture(action);
            }
        });
        return;
    }

    // 2. 自動從文本檢測手勢
    const detectedGesture = detectGestureFromText(text);
    if (detectedGesture) {
        playGesture(detectedGesture);
    }
}

// ============================================
// AI 自主動作設計系統 (AI Gesture Code Generator)
// ============================================

// VRM 骨骼參數說明（供 AI 參考）
const BoneDocumentation = {
    // 頭部
    head: {
        description: '頭部',
        x: '上下點頭 (-0.3 低頭, 0.3 抬頭)',
        y: '左右轉頭 (-0.4 左轉, 0.4 右轉)',
        z: '歪頭 (-0.2 右歪, 0.2 左歪)'
    },
    // 脊椎
    spine: {
        description: '上半身/脊椎',
        x: '鞠躬 (0.3 向前彎)',
        y: '扭腰 (-0.2 左扭, 0.2 右扭)',
        z: '側彎'
    },
    // 手臂
    rightUpperArm: {
        description: '右上臂',
        x: '舉手高度 (-1.5 舉高, 0 放下)',
        y: '向前/向後',
        z: '向側邊 (0.5 張開)'
    },
    leftUpperArm: {
        description: '左上臂',
        x: '舉手高度 (-1.5 舉高, 0 放下)',
        y: '向前/向後',
        z: '向側邊 (-0.5 張開)'
    },
    // 肩膀
    rightShoulder: { description: '右肩', y: '聳肩 (0.2 上抬)' },
    leftShoulder: { description: '左肩', y: '聳肩 (0.2 上抬)' },
    // 位移
    offset: { description: '整體位移', y: '跳躍 (0.03 跳起)' },
};

// 動態註冊的手勢
const DynamicGestures = {};

/**
 * 解析 AI 生成的手勢程式碼並註冊
 * 格式: [GESTURE_CODE:name]JSON_KEYFRAMES[/GESTURE_CODE]
 * 
 * 例如:
 * [GESTURE_CODE:heart]
 * {
 *   "duration": 1.5,
 *   "keyframes": [
 *     {"t": 0, "rightUpperArm": {"x": 0, "z": 0}, "leftUpperArm": {"x": 0, "z": 0}},
 *     {"t": 0.5, "rightUpperArm": {"x": -1.2, "z": 0.3}, "leftUpperArm": {"x": -1.2, "z": -0.3}},
 *     {"t": 1.0, "rightUpperArm": {"x": -1.2, "z": 0.5}, "leftUpperArm": {"x": -1.2, "z": -0.5}},
 *     {"t": 1.5, "rightUpperArm": {"x": 0, "z": 0}, "leftUpperArm": {"x": 0, "z": 0}}
 *   ]
 * }
 * [/GESTURE_CODE]
 */
function parseAndRegisterNewGestures(text) {
    console.log('🔍 Parsing text for gestures...');

    // 簡化的正則：匹配 [GESTURE_CODE:任何內容] 後的 JSON
    // 使用非貪婪匹配找到第一個完整的 JSON 對象
    const regex = /\[GESTURE_CODE:([^\]]+)\]\s*(\{[^}]*"keyframes"\s*:\s*\[[^\]]*\][^}]*\})/gi;

    let matches = [...text.matchAll(regex)];

    // 備用方案：如果上面沒匹配到，嘗試更簡單的方式
    if (matches.length === 0) {
        // 找 [GESTURE_CODE:...] 然後提取後面的 {...}
        const simpleMatch = text.match(/\[GESTURE_CODE:([^\]]+)\]\s*(\{[\s\S]{10,300}?\}\s*\]?\s*\})/i);
        if (simpleMatch) {
            matches = [[simpleMatch[0], simpleMatch[1], simpleMatch[2]]];
        }
    }

    console.log('Found', matches.length, 'gesture matches');

    for (const match of matches) {
        // 清理名稱（中文轉拼音風格的 _）
        let rawName = match[1].trim();
        let gestureName = rawName.replace(/[^\w]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '') || 'custom';

        let jsonString = match[2].trim();
        console.log('Parsing gesture:', rawName, '→', gestureName);
        console.log('JSON:', jsonString.substring(0, 100) + '...');

        try {
            // 智慧 JSON 提取：計算括號來找到有效的 JSON 結尾
            const cleanedJSON = extractValidJSON(jsonString);
            console.log('Cleaned JSON:', cleanedJSON.substring(0, 100) + '...');

            const animData = JSON.parse(cleanedJSON);

            // 驗證格式
            if (!animData.duration || !animData.keyframes) {
                console.warn('Invalid gesture format:', gestureName);
                continue;
            }

            // 註冊新手勢
            DynamicGestures[gestureName] = animData;
            GestureAnimations[gestureName] = animData;

            console.log(`🎨 AI 創建新手勢: ${gestureName}`, animData);

            // 自動播放新創建的手勢
            setTimeout(() => playGesture(gestureName), 100);

        } catch (e) {
            console.error('Failed to parse gesture code:', e.message);
        }
    }
}

/**
 * 智慧提取 JSON：通過計算括號找到有效的 JSON 邊界
 */
function extractValidJSON(str) {
    let depth = 0;
    let inString = false;
    let escape = false;
    let start = str.indexOf('{');

    if (start === -1) return str;

    for (let i = start; i < str.length; i++) {
        const char = str[i];

        if (escape) {
            escape = false;
            continue;
        }

        if (char === '\\') {
            escape = true;
            continue;
        }

        if (char === '"' && !escape) {
            inString = !inString;
            continue;
        }

        if (!inString) {
            if (char === '{') depth++;
            if (char === '}') {
                depth--;
                if (depth === 0) {
                    return str.substring(start, i + 1);
                }
            }
        }
    }

    return str; // 如果沒找到完整的 JSON，返回原字串讓它失敗
}

/**
 * 為 AI 生成手勢創建的提示詞
 * 這個函數返回一個系統提示，教 AI 如何創建手勢
 */
function getGestureCreationPrompt() {
    return `
你可以創建自定義動畫！使用以下格式：

[GESTURE_CODE:動作名稱]
{
  "duration": 秒數,
  "keyframes": [
    {"t": 時間點, "骨骼名": {"x": 角度, "y": 角度, "z": 角度}},
    ...
  ]
}
[/GESTURE_CODE]

可用骨骼:
- head: 頭部 (x=點頭, y=轉頭, z=歪頭)
- spine: 脊椎 (x=鞠躬)
- rightUpperArm/leftUpperArm: 手臂 (x=舉手, z=張開)
- rightShoulder/leftShoulder: 肩膀 (y=聳肩)
- offset: 位移 (y=跳躍)

角度範圍: -1.5 到 1.5 (弧度)
時間點: 0 到 duration

範例 - 比心動作:
[GESTURE_CODE:heart]
{
  "duration": 2.0,
  "keyframes": [
    {"t": 0, "rightUpperArm": {"x": 0, "z": 0}, "leftUpperArm": {"x": 0, "z": 0}},
    {"t": 0.5, "rightUpperArm": {"x": -1.0, "y": 0.5}, "leftUpperArm": {"x": -1.0, "y": -0.5}},
    {"t": 1.5, "rightUpperArm": {"x": -1.0, "y": 0.5}, "leftUpperArm": {"x": -1.0, "y": -0.5}},
    {"t": 2.0, "rightUpperArm": {"x": 0, "z": 0}, "leftUpperArm": {"x": 0, "z": 0}}
  ]
}
[/GESTURE_CODE]

創建動作後使用 [ACTION:動作名稱] 來播放。
`;
}

// 匯出骨骼文檔供 AI 使用
window.BoneDocumentation = BoneDocumentation;
window.getGestureCreationPrompt = getGestureCreationPrompt;

const conversationHistory = [];

function recordConversation(role, content) {
    if (!content || !role) return;
    conversationHistory.push({ role, content });
    if (conversationHistory.length > CONFIG.HISTORY_LIMIT) {
        conversationHistory.splice(0, conversationHistory.length - CONFIG.HISTORY_LIMIT);
    }
}

function getHistoryForRequest(currentMessage) {
    if (!conversationHistory.length) return [];
    const last = conversationHistory[conversationHistory.length - 1];
    if (last.role === 'user' && last.content === currentMessage) {
        return conversationHistory.slice(0, -1);
    }
    return conversationHistory.slice();
}

function buildApiUrl(path) {
    if (!path) return CONFIG.API_URL;
    return path.startsWith('/') ? `${CONFIG.API_URL}${path}` : `${CONFIG.API_URL}/${path}`;
}

// ============================================
// 對話系統 - 雙模型架構
// ============================================

/**
 * 雙模型架構：
 * 1. 動作模型 (Action Model) - 只負責決定角色動作和表情
 * 2. 對話模型 (Dialogue Model) - 只負責生成角色對話
 * 兩者並行執行，各司其職
 */
async function sendMessage(text) {
    if (!text.trim()) return;

    addMessage(text, 'user');
    document.getElementById('user-input').value = '';

    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;

    // 進入思考狀態
    transitionTo(CharacterState.THINKING);
    updateServiceStatus('TS007', 'processing');

    try {
        const history = getHistoryForRequest(text);
        const toneSoulResult = await callToneSoulAPI(text, history);

        if (toneSoulResult && toneSoulResult.content) {
            if (toneSoulResult.gesture) {
                playGesture(toneSoulResult.gesture);
            }
            if (toneSoulResult.expression) {
                setExpression(toneSoulResult.expression);
            }

            executeAIActions(toneSoulResult.content);
            startSpeaking(toneSoulResult.content);
            addMessage(toneSoulResult.content, 'assistant');

            if (toneSoulResult.monitor) {
                console.log('Monitor:', toneSoulResult.monitor);
            }
            updateServiceStatus('TS007', 'ready');
        } else {
            const [actionResult, dialogueResult] = await Promise.all([
                callActionModel(text),
                callDialogueModel(text)
            ]);

            console.log('Action Model:', actionResult);
            console.log('Dialogue Model:', dialogueResult);

            if (actionResult.gesture) {
                playGesture(actionResult.gesture);
            }
            if (actionResult.expression) {
                setExpression(actionResult.expression);
            }

            executeAIActions(dialogueResult.content);
            startSpeaking(dialogueResult.content);

            if (dialogueResult.emotion && !actionResult.expression) {
                setExpression(dialogueResult.emotion);
            }

            addMessage(dialogueResult.content, 'assistant');
            updateServiceStatus('TS007', 'ready');
        }

    } catch (error) {
        console.error('API Error:', error);
        const fallback = generateFallbackResponse(text);
        addMessage(fallback, 'assistant');
        startSpeaking(fallback);
        updateServiceStatus('TS007', 'fallback');
    }

    sendBtn.disabled = false;
}

/**
 * 動作模型 - 專門決定角色動作和表情
 * 只輸出結構化的動作指令，不輸出對話
 */
async function callActionModel(userInput) {
    const systemPrompt = `你是一個動作控制器，負責決定角色應該做什麼動作和表情。

角色：牧瀨紅莉栖 - 傲嬌天才科學家

根據用戶說的話，輸出最適合的動作和表情。只輸出 JSON，不要說任何其他話：

{
  "gesture": "動作名稱",
  "expression": "表情名稱", 
  "reason": "選擇原因"
}

可用動作: nod(點頭), shake(搖頭), wave(揮手), bow(鞠躬), shrug(聳肩), thinking(思考), happy(開心)
可用表情: neutral(中性), happy(開心), angry(生氣), sad(難過), relaxed(放鬆), surprised(驚訝)

例如：
- 用戶說"你好" → {"gesture": "wave", "expression": "happy", "reason": "打招呼"}
- 用戶稱讚你 → {"gesture": "nod", "expression": "happy", "reason": "害羞接受"}
- 用戶問問題 → {"gesture": "thinking", "expression": "neutral", "reason": "認真思考"}`;

    try {
        const response = await fetch(`${CONFIG.OLLAMA_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: CONFIG.OLLAMA_MODEL,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: userInput }
                ],
                stream: false,
                options: { temperature: 0.3 }  // 低溫度讓輸出更穩定
            })
        });

        const data = await response.json();
        const content = data.message?.content || '';

        // 提取 JSON
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]);
        }
    } catch (e) {
        console.warn('Action model failed:', e);
    }

    // 失敗時返回預設
    return { gesture: null, expression: 'neutral' };
}

/**
 * 對話模型 - 專門生成角色對話
 * 只輸出自然語言，不需要處理動作
 */
async function callDialogueModel(userInput) {
    const systemPrompt = `你是「牧瀨紅莉栖」(Makise Kurisu)，一位天才科學家。

性格：
- 傲嬌但善良，經常嘴硬心軟
- 聰明且有邏輯，喜歡科學思考
- 有時會害羞，特別是被誇獎時

說話風格：
- 用中文回答
- 偶爾傲嬌台詞如「哼、才不是那樣呢！」
- 回答要簡潔，2-3 句話
- 不要輸出任何動作指令，只說話`;

    try {
        const response = await fetch(`${CONFIG.OLLAMA_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: CONFIG.OLLAMA_MODEL,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: userInput }
                ],
                stream: false
            })
        });

        const data = await response.json();
        return {
            content: data.message?.content || '...',
            emotion: detectEmotionFromText(data.message?.content || '')
        };
    } catch (e) {
        console.error('Dialogue model failed:', e);
        return { content: '...連線有點問題呢', emotion: 'neutral' };
    }
}

/**
 * 從文本檢測情緒
 */
function detectEmotionFromText(text) {
    const emotionKeywords = {
        happy: ['開心', '快樂', '太棒', '哈哈', '嘻嘻', '棒', '好玩'],
        angry: ['哼', '才不是', '煩', '討厭', '笨蛋', '生氣'],
        sad: ['難過', '傷心', '抱歉', '對不起', '唉'],
        surprised: ['哇', '天啊', '真的嗎', '咦', '欸'],
        relaxed: ['嗯', '好吧', '隨便', '都可以']
    };

    for (const [emotion, keywords] of Object.entries(emotionKeywords)) {
        for (const keyword of keywords) {
            if (text.includes(keyword)) {
                return emotion;
            }
        }
    }
    return 'neutral';
}

async function callToneSoulAPI(text, history) {
    try {
        const response = await fetch(buildApiUrl(CONFIG.VRM_API_PATH), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: Array.isArray(history) ? history : [],
                persona: CONFIG.PERSONA_ID
            })
        });

        if (!response.ok) return null;
        const data = await response.json();
        return {
            content: data.response || data.content || '',
            gesture: data.gesture || null,
            expression: data.expression || null,
            monitor: data.monitor || null,
        };
    } catch (e) {
        console.log('ToneSoul API not available:', e);
        return null;
    }
}

async function callOllamaDirectly(text) {
    const systemPrompt = `你是「牧瀨紅莉栖」(Makise Kurisu)，一位天才科學家，現在有了一個 3D 虛擬身體。

性格：
- 傲嬌但善良，經常嘴硬心軟
- 聰明且有邏輯，喜歡科學思考
- 有時會害羞，特別是被誇獎時

說話風格：
- 用中文回答，偶爾傲嬌台詞
- 回答要簡潔，3-4 句話為主

動作控制：
- 使用 [ACTION:nod/shake/wave/bow/shrug/thinking/happy] 做預設動作
- 你也可以創建新動作！格式：

[GESTURE_CODE:動作名]
{"duration": 秒數, "keyframes": [{"t": 時間, "骨骼": {"x": 角度}}...]}
[/GESTURE_CODE]

可用骨骼: head(頭), spine(脊椎), rightUpperArm/leftUpperArm(手臂), offset(跳躍)
角度範圍: -1.5 到 1.5

如果用戶要求做動作，請創建並使用！例如用戶說「比心」，你可以創建 heart 動作。`;

    try {
        const response = await fetch(`${CONFIG.OLLAMA_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: 'gemma3:4b',
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: text }
                ],
                stream: false
            })
        });

        if (response.ok) {
            const data = await response.json();
            return {
                content: data.message.content,
                emotion: detectEmotion(data.message.content)
            };
        }
    } catch (e) {
        console.error('Ollama error:', e);
    }

    throw new Error('No backend available');
}

function generateFallbackResponse(text) {
    const responses = [
        '哼、我現在沒辦法連接到我的大腦處理器呢... 你有確認 Ollama 在運行嗎？',
        '等等，網路連線好像有問題。才、才不是我故意不回答你的！',
        '系統異常... 請確認後端服務是否正常。不要誤會，我只是在說明狀況而已！',
    ];
    return responses[Math.floor(Math.random() * responses.length)];
}

function detectEmotion(text) {
    if (/傲嬌|哼|才不是|什麼嘛/.test(text)) return 'angry';
    if (/開心|高興|太棒|有趣|好玩/.test(text)) return 'happy';
    if (/抱歉|難過|遺憾|可惜/.test(text)) return 'sad';
    if (/驚訝|什麼|真的嗎|怎麼可能/.test(text)) return 'surprised';
    if (/害羞|那個|嗯|這個/.test(text)) return 'relaxed';
    return 'neutral';
}

function addMessage(text, role, trackHistory = true) {
    const chatHistory = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.textContent = text;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    if (trackHistory) {
        recordConversation(role, text);
    }
}

// ============================================
// UI 事件
// ============================================
function setupEventListeners() {
    document.getElementById('send-btn').addEventListener('click', () => {
        const input = document.getElementById('user-input');
        sendMessage(input.value);
    });

    document.getElementById('user-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(e.target.value);
        }
    });

    document.querySelectorAll('.expr-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.expr-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            setExpression(btn.dataset.expr);
        });
    });

    // 頭部追蹤：監聽滑鼠移動
    const canvas = document.getElementById('vrm-canvas');
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mousePosition.x = (e.clientX - rect.left) / rect.width;
        mousePosition.y = (e.clientY - rect.top) / rect.height;
    });

    // 雙擊切換追蹤
    canvas.addEventListener('dblclick', () => {
        toggleMouseTracking(!isMouseTracking);
    });
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function updateLoadingText(text) {
    const loadingText = document.querySelector('.loading-text');
    if (loadingText) loadingText.textContent = text;
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
        setTimeout(() => overlay.remove(), 500);
    }
    isLoading = false;
}

function getVRMStatus() {
    return {
        ...vrmStatus,
        loaded: !!currentVRM,
    };
}

async function reloadVRM(url) {
    return loadVRM(url || CONFIG.DEFAULT_VRM);
}

// ============================================
// 啟動
// ============================================
init().catch(error => {
    console.error('Init error:', error);
    updateLoadingText('載入失敗，請重新整理頁面');
});

// 匯出給全域使用
window.ToneSoul = {
    setExpression,
    startSpeaking,
    stopSpeaking,
    transitionTo,
    CharacterState,
    ServiceCode,
    // 手勢控制
    playGesture,
    GestureType,
    toggleMouseTracking,
    // VRM status
    getVRMStatus,
    reloadVRM,
};
