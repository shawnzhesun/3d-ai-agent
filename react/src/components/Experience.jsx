import { Environment, OrbitControls, useTexture } from "@react-three/drei";
import { AvatarBase } from "./AvatarBase";
import { useThree } from "@react-three/fiber";

export const Experience = ({index}) => {
  var texture = useTexture(`/textures/bg${index}.png`);
  var viewport = useThree((state) => state.viewport);
  return (
    <>
      <AvatarBase modelPath={`/models/model${index}.glb`} audioControlName={`playAudio${index}`} scriptControlName={`script${index}`} position={[-0.3, -3.25, 5]} scale={2}/>
      <Environment preset="sunset" />
      <mesh>
        <planeGeometry args={[viewport.width, viewport.height]} />
        <meshBasicMaterial map={texture} />
      </mesh>
    </>
  );
};
