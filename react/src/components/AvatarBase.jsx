import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useAnimations, useFBX, useGLTF } from '@react-three/drei';
import { useControls } from 'leva';
import { useFrame, useLoader } from '@react-three/fiber';
import * as THREE from 'three';
import Dialogue from './Dialogue';

const mouthCueMapping = {
  A: "viseme_PP",
  B: "viseme_kk",
  C: "viseme_I",
  D: "viseme_AA",
  E: "viseme_O",
  F: "viseme_U",
  G: "viseme_FF",
  H: "viseme_TH",
  X: "viseme_PP",
};

export function AvatarBase({ modelPath, audioControlName, scriptControlName, ...props }) {
  const { nodes, materials } = useGLTF(modelPath);
  const { animations: IdleAnimation } = useFBX('/animations/Idle.fbx');
  const { animations: SaluteAnimation } = useFBX('/animations/Salute.fbx');

  const controlConfig = {};
  controlConfig[audioControlName] = false;
  controlConfig[scriptControlName] = {
    value: 'newMessage',
    options: ['newMessage']
  };

  const { [audioControlName]: playAudio, [scriptControlName]: script } = useControls(controlConfig);

  const audio = useMemo(() => new Audio(`/audios/${script}.mp3`), [script]);
  const jsonFile = useLoader(THREE.FileLoader, `/audios/${script}.json`);
  const lipSync = JSON.parse(jsonFile);

  useFrame(() => {
    const currentAudioTime = audio.currentTime
    if (audio.paused || audio.ended) {
      setAnimation('Idle')
      setShowDialogue(false)
    }
    Object.values(mouthCueMapping).forEach((key) => {
      nodes.Wolf3D_Head.morphTargetInfluences[nodes.Wolf3D_Head.morphTargetDictionary[key]] = 0
      nodes.Wolf3D_Teeth.morphTargetInfluences[nodes.Wolf3D_Teeth.morphTargetDictionary[key]] = 0
    })
    for(let i = 0; i < lipSync.mouthCues.length; i++) {
      const mouthCue = lipSync.mouthCues[i]
      if (currentAudioTime >= mouthCue.start && currentAudioTime <= mouthCue.end) {
        nodes.Wolf3D_Head.morphTargetInfluences[nodes.Wolf3D_Head.morphTargetDictionary[mouthCueMapping[mouthCue.value]]] = 1
        nodes.Wolf3D_Teeth.morphTargetInfluences[nodes.Wolf3D_Teeth.morphTargetDictionary[mouthCueMapping[mouthCue.value]]] = 1
        break
      }
    }
  })

  useEffect(() => {
    if (playAudio) {
      audio.play()
      setShowDialogue(true)
      if (script == 'newMessage') {
        setAnimation('Salute')
      } else {
        setAnimation('Idle')
      }
    } else {
      setAnimation('Idle')
      audio.pause()
    }
  }, [playAudio, script])

  IdleAnimation[0].name = 'Idle'
  SaluteAnimation[0].name = 'Salute'

  const group = useRef()
  const [animation, setAnimation] = useState('Idle')
  const [showDialogue, setShowDialogue] = useState(false)
  const { actions } = useAnimations([IdleAnimation[0], SaluteAnimation[0]], group)

  useEffect(() => {
    actions[animation].reset().fadeIn(0.5).play()
    return () => actions[animation].fadeOut(0.5)
  }, [animation])

  useEffect(() => {
    nodes.Wolf3D_Head.morphTargetInfluences[nodes.Wolf3D_Head.morphTargetDictionary['viseme_O']] = 1
    nodes.Wolf3D_Teeth.morphTargetInfluences[nodes.Wolf3D_Teeth.morphTargetDictionary['viseme_O']] = 1
  }, [])

  useFrame((state) => {
    // group.current.rotation.y = 1; // turn to theright
    group.current.getObjectByName("Head").lookAt(state.camera.position);
  });

  return (
    <>
      <group {...props} dispose={null} ref={group}>
        <primitive object={nodes.Hips} />
        <skinnedMesh
          name="EyeLeft"
          geometry={nodes.EyeLeft.geometry}
          material={materials.Wolf3D_Eye}
          skeleton={nodes.EyeLeft.skeleton}
          morphTargetDictionary={nodes.EyeLeft.morphTargetDictionary}
          morphTargetInfluences={nodes.EyeLeft.morphTargetInfluences}
        />
        <skinnedMesh
          name="EyeRight"
          geometry={nodes.EyeRight.geometry}
          material={materials.Wolf3D_Eye}
          skeleton={nodes.EyeRight.skeleton}
          morphTargetDictionary={nodes.EyeRight.morphTargetDictionary}
          morphTargetInfluences={nodes.EyeRight.morphTargetInfluences}
        />
        <skinnedMesh
          name="Wolf3D_Head"
          geometry={nodes.Wolf3D_Head.geometry}
          material={materials.Wolf3D_Skin}
          skeleton={nodes.Wolf3D_Head.skeleton}
          morphTargetDictionary={nodes.Wolf3D_Head.morphTargetDictionary}
          morphTargetInfluences={nodes.Wolf3D_Head.morphTargetInfluences}
        />
        <skinnedMesh
          name="Wolf3D_Teeth"
          geometry={nodes.Wolf3D_Teeth.geometry}
          material={materials.Wolf3D_Teeth}
          skeleton={nodes.Wolf3D_Teeth.skeleton}
          morphTargetDictionary={nodes.Wolf3D_Teeth.morphTargetDictionary}
          morphTargetInfluences={nodes.Wolf3D_Teeth.morphTargetInfluences}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Hair.geometry}
          material={materials.Wolf3D_Hair}
          skeleton={nodes.Wolf3D_Hair.skeleton}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Body.geometry}
          material={materials.Wolf3D_Body}
          skeleton={nodes.Wolf3D_Body.skeleton}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Outfit_Bottom.geometry}
          material={materials.Wolf3D_Outfit_Bottom}
          skeleton={nodes.Wolf3D_Outfit_Bottom.skeleton}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Outfit_Footwear.geometry}
          material={materials.Wolf3D_Outfit_Footwear}
          skeleton={nodes.Wolf3D_Outfit_Footwear.skeleton}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Outfit_Top.geometry}
          material={materials.Wolf3D_Outfit_Top}
          skeleton={nodes.Wolf3D_Outfit_Top.skeleton}
        />
      </group>
      <Dialogue message="Hi! This is Shawn, I have something to share with you." position={[0.5, 0.2, 5]} visible={showDialogue} />
    </>
  );
}

useGLTF.preload('/models/model1.glb');
useGLTF.preload('/models/model2.glb');
useGLTF.preload('/models/model3.glb');
useGLTF.preload('/models/model4.glb');