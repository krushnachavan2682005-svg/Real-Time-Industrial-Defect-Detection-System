import React, { useRef, useState, useEffect } from 'react';
import type { DefectSchema } from '../types';

interface Props {
  imageUrl: string;
  defects: DefectSchema[];
}

export const BoundingBoxOverlay: React.FC<Props> = ({ imageUrl, defects }) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const [scale, setScale] = useState({ x: 1, y: 1 });

  const handleImageLoad = () => {
    if (imgRef.current) {
      const { naturalWidth, naturalHeight, width, height } = imgRef.current;
      // Safeguard against zero division
      if (naturalWidth > 0 && naturalHeight > 0) {
        setScale({
          x: width / naturalWidth,
          y: height / naturalHeight,
        });
      }
    }
  };

  useEffect(() => {
    const handleResize = () => handleImageLoad();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="bbox-container">
      <img 
        ref={imgRef} 
        src={imageUrl} 
        alt="Surface Inspection" 
        onLoad={handleImageLoad} 
      />
      {defects.map((defect, idx) => {
        const { bbox, class_name, confidence } = defect;
        const left = bbox.x1 * scale.x;
        const top = bbox.y1 * scale.y;
        const boxWidth = (bbox.x2 - bbox.x1) * scale.x;
        const boxHeight = (bbox.y2 - bbox.y1) * scale.y;

        return (
          <div
            key={idx}
            className="bbox"
            style={{
              left: `${left}px`,
              top: `${top}px`,
              width: `${boxWidth}px`,
              height: `${boxHeight}px`,
            }}
          >
            <div className="bbox-label">
              {class_name} ({(confidence * 100).toFixed(0)}%)
            </div>
          </div>
        );
      })}
    </div>
  );
};
