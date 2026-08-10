import * as THREE from "three";

const DISC_TEXTURE = "/images/nomos-golden-record-disc.png";

/**
 * Face-on square crop of the Voyager record so UV mapping stays circular
 * (the landscape source was stretching into a clipped ellipse).
 */
export function loadGoldenRecordTexture(
  loader: THREE.TextureLoader = new THREE.TextureLoader()
): THREE.Texture {
  const texture = loader.load(DISC_TEXTURE);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 8;
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.center.set(0.5, 0.5);
  texture.repeat.set(0.94, 0.94);
  return texture;
}

/**
 * Premium 3D record: camera-facing circular face + metal rim + halo ring.
 * Animate the returned `disc` group (not individual meshes) so tilt never
 * collapses the face into an edge-on line.
 */
export function createGoldenRecordDisc(texture: THREE.Texture): {
  disc: THREE.Group;
  ring: THREE.Mesh;
} {
  const disc = new THREE.Group();

  const faceMat = new THREE.MeshStandardMaterial({
    map: texture,
    metalness: 0.9,
    roughness: 0.24,
    emissive: new THREE.Color("#3d3010"),
    emissiveIntensity: 0.14,
    side: THREE.FrontSide
  });
  const metalMat = new THREE.MeshStandardMaterial({
    color: 0xb8922e,
    metalness: 0.96,
    roughness: 0.22
  });
  const backMat = new THREE.MeshStandardMaterial({
    color: 0x7a5f18,
    metalness: 0.92,
    roughness: 0.35
  });

  const radius = 1.12;
  const thickness = 0.05;

  const face = new THREE.Mesh(new THREE.CircleGeometry(radius, 128), faceMat);
  face.position.z = thickness / 2;

  const back = new THREE.Mesh(new THREE.CircleGeometry(radius, 128), backMat);
  back.rotation.y = Math.PI;
  back.position.z = -thickness / 2;

  const rim = new THREE.Mesh(
    new THREE.CylinderGeometry(radius, radius, thickness, 128, 1, true),
    metalMat
  );
  rim.rotation.x = Math.PI / 2;

  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(radius + 0.14, 0.015, 12, 128),
    new THREE.MeshStandardMaterial({
      color: 0xe3c05c,
      metalness: 0.85,
      roughness: 0.3,
      transparent: true,
      opacity: 0.5
    })
  );

  disc.add(face, back, rim, ring);
  // Keep the full engraved face inside the circular stage with a metal lip.
  disc.scale.setScalar(0.88);
  return { disc, ring };
}
