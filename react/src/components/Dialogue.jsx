import React from 'react';
import { Sphere } from '@react-three/drei';
import { Text } from '@react-three/drei';

const Dialogue = ({ message, position, visible }) => {
  const bubblePosition = position;
  const bubbleDiameter = 1;
  const bubblePadding = 0.1;
  const maxLineWidth = bubbleDiameter - bubblePadding;

  const wrapText = (text, maxCharsPerLine) => {
    const words = text.split(' ');
    let wrappedText = '';
    let currentLine = '';

    words.forEach(word => {
      if ((currentLine + word).length > maxCharsPerLine) {
        wrappedText += `${currentLine}\n`;
        currentLine = '';
      }
      currentLine += `${word} `;
    });

    wrappedText += currentLine; // Add any remaining text in the current line
    return wrappedText.trim();
};


  const maxCharsPerLine = 30;
  const wrappedMessage = wrapText(message, maxCharsPerLine);

  return (
    <>
      <Sphere args={[bubbleDiameter/2, 32, 32]} position={bubblePosition} visible={visible}>
        <meshBasicMaterial attach="material" color="white" transparent opacity={0.8} />
      </Sphere>

      <Text
        position={[position[0]-0.1, position[1], position[2] + 0.5]}
        fontSize={0.05}
        color="#000"
        maxWidth={maxLineWidth}
        visible={visible}
      >
        {wrappedMessage}
      </Text>
    </>
  );
};

export default Dialogue;