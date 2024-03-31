import { Canvas } from "@react-three/fiber";
import { Experience } from "./components/Experience";

function App() {
  return (
    <div className="canvasContainer">
      <Canvas shadows camera={{ position: [0, 0, 8], fov: 30 }}>
        <color attach="background" args={["#ececec"]} />
        <Experience index={1}/>
      </Canvas>
      <Canvas shadows camera={{ position: [0, 0, 8], fov: 30 }}>
        <color attach="background" args={["#ececec"]} />
        <Experience index={2} />
      </Canvas>
      <Canvas shadows camera={{ position: [0, -0.25, 8], fov: 30 }}>
        <color attach="background" args={["#ececec"]} />
        <Experience index={3}/>
      </Canvas>
      <Canvas shadows camera={{ position: [0, 0, 8], fov: 30 }}>
        <color attach="background" args={["#ececec"]} />
        <Experience index={4}/>
      </Canvas>
    </div>
  );
}

export default App;
