"use client";

import type { FeatureCollection, Geometry } from "geojson";
import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import world from "world-atlas/countries-110m.json";

import type { GroundStation } from "@/lib/types";

const GLOBE_RADIUS = 1.5;

function toGlobePoint(latitude: number, longitude: number, radius = GLOBE_RADIUS) {
  const phi = THREE.MathUtils.degToRad(90 - latitude);
  const theta = THREE.MathUtils.degToRad(longitude + 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function addCountryLines(group: THREE.Group) {
  const topology = world as unknown as Topology<{
    countries: GeometryCollection;
  }>;
  const countries = feature(
    topology,
    topology.objects.countries
  ) as unknown as FeatureCollection<Geometry>;
  const material = new THREE.LineBasicMaterial({
    color: new THREE.Color("#d7d1c5"),
    opacity: 0.42,
    transparent: true
  });

  const addRing = (ring: number[][]) => {
    const points: THREE.Vector3[] = [];
    ring.forEach(([longitude, latitude], index) => {
      const previous = ring[index - 1];
      if (previous && Math.abs(previous[0] - longitude) > 180) {
        if (points.length > 1) {
          group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points.splice(0)), material));
        }
      }
      points.push(toGlobePoint(latitude, longitude, GLOBE_RADIUS * 1.003));
    });
    if (points.length > 1) {
      group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), material));
    }
  };

  countries.features.forEach((country) => {
    const geometry = country.geometry;
    if (geometry.type === "Polygon") {
      geometry.coordinates.forEach(addRing);
    } else if (geometry.type === "MultiPolygon") {
      geometry.coordinates.forEach((polygon) => polygon.forEach(addRing));
    }
  });
}

function addGraticule(group: THREE.Group) {
  const material = new THREE.LineBasicMaterial({
    color: new THREE.Color("#e3c05c"),
    opacity: 0.13,
    transparent: true
  });
  for (let latitude = -60; latitude <= 60; latitude += 30) {
    const points: THREE.Vector3[] = [];
    for (let longitude = -180; longitude <= 180; longitude += 3) {
      points.push(toGlobePoint(latitude, longitude, GLOBE_RADIUS * 1.006));
    }
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), material));
  }
  for (let longitude = -150; longitude < 180; longitude += 30) {
    const points: THREE.Vector3[] = [];
    for (let latitude = -90; latitude <= 90; latitude += 3) {
      points.push(toGlobePoint(latitude, longitude, GLOBE_RADIUS * 1.006));
    }
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), material));
  }
}

export function GroundNetworkGlobe({
  stations,
  selectedId,
  onSelect
}: {
  stations: GroundStation[];
  selectedId: string;
  onSelect: (stationId: string) => void;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const selectedRef = useRef(selectedId);
  const onSelectRef = useRef(onSelect);

  useEffect(() => {
    selectedRef.current = selectedId;
  }, [selectedId]);

  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      container.dataset.webgl = "unavailable";
      return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.setAttribute("aria-label", "Interactive three-dimensional ground network globe");
    renderer.domElement.setAttribute("role", "img");
    renderer.domElement.style.display = "block";
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 50);
    camera.position.set(0, 0.2, 5.4);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.enablePan = false;
    controls.minDistance = 3.4;
    controls.maxDistance = 8;
    controls.rotateSpeed = 0.45;
    controls.zoomSpeed = 0.7;

    const globe = new THREE.Group();
    globe.rotation.y = THREE.MathUtils.degToRad(-12);
    globe.rotation.x = THREE.MathUtils.degToRad(-7);
    scene.add(globe);

    globe.add(
      new THREE.Mesh(
        new THREE.SphereGeometry(GLOBE_RADIUS, 96, 96),
        new THREE.MeshPhongMaterial({
          color: new THREE.Color("#123da5"),
          emissive: new THREE.Color("#001045"),
          emissiveIntensity: 0.55,
          shininess: 10,
          specular: new THREE.Color("#536bb7")
        })
      )
    );
    globe.add(
      new THREE.Mesh(
        new THREE.SphereGeometry(GLOBE_RADIUS * 1.055, 72, 72),
        new THREE.MeshBasicMaterial({
          color: new THREE.Color("#315ddd"),
          opacity: 0.09,
          side: THREE.BackSide,
          transparent: true
        })
      )
    );
    addGraticule(globe);
    addCountryLines(globe);

    scene.add(new THREE.AmbientLight(new THREE.Color("#8d9bca"), 1.55));
    const keyLight = new THREE.DirectionalLight(new THREE.Color("#f4efe6"), 2.2);
    keyLight.position.set(4, 3, 5);
    scene.add(keyLight);
    const rimLight = new THREE.DirectionalLight(new THREE.Color("#e3c05c"), 1.15);
    rimLight.position.set(-4, -1, -2);
    scene.add(rimLight);

    const markerMeshes: THREE.Mesh[] = [];
    const markerMaterial = new THREE.MeshBasicMaterial({ color: new THREE.Color("#e3c05c") });
    stations.forEach((station) => {
      const point = toGlobePoint(station.latitude, station.longitude, GLOBE_RADIUS * 1.03);
      const normal = point.clone().normalize();
      const marker = new THREE.Mesh(new THREE.SphereGeometry(0.045, 20, 20), markerMaterial.clone());
      marker.position.copy(point);
      marker.userData.stationId = station.id;
      globe.add(marker);
      markerMeshes.push(marker);

      const stemGeometry = new THREE.BufferGeometry().setFromPoints([
        point.clone().multiplyScalar(0.995),
        point.clone().add(normal.multiplyScalar(0.13))
      ]);
      globe.add(
        new THREE.Line(
          stemGeometry,
          new THREE.LineBasicMaterial({ color: new THREE.Color("#e3c05c"), opacity: 0.72, transparent: true })
        )
      );
    });

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const updatePointer = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    };
    const hitStation = () => {
      raycaster.setFromCamera(pointer, camera);
      return raycaster.intersectObjects(markerMeshes, false)[0]?.object as THREE.Mesh | undefined;
    };
    const onPointerMove = (event: PointerEvent) => {
      updatePointer(event);
      renderer.domElement.style.cursor = hitStation() ? "pointer" : "grab";
    };
    const onPointerDown = (event: PointerEvent) => {
      updatePointer(event);
      const hit = hitStation();
      if (hit?.userData.stationId) onSelectRef.current(String(hit.userData.stationId));
    };
    renderer.domElement.addEventListener("pointermove", onPointerMove);
    renderer.domElement.addEventListener("pointerdown", onPointerDown);

    const resize = () => {
      if (!container.clientWidth || !container.clientHeight) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight, false);
    };
    resize();
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);

    let frame = 0;
    let visible = true;
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
    });
    observer.observe(container);
    const animate = () => {
      if (visible) {
        controls.update();
        markerMeshes.forEach((marker) => {
          const selected = marker.userData.stationId === selectedRef.current;
          marker.scale.setScalar(selected ? 1.55 : 1);
          (marker.material as THREE.MeshBasicMaterial).color.set(selected ? "#f4efe6" : "#e3c05c");
        });
        renderer.render(scene, camera);
      }
      frame = window.requestAnimationFrame(animate);
    };
    frame = window.requestAnimationFrame(animate);

    return () => {
      window.cancelAnimationFrame(frame);
      observer.disconnect();
      resizeObserver.disconnect();
      controls.dispose();
      renderer.domElement.removeEventListener("pointermove", onPointerMove);
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh || object instanceof THREE.Line) {
          object.geometry.dispose();
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          materials.forEach((material) => material.dispose());
        }
      });
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, [stations]);

  return <div className="ground-globe" ref={containerRef} />;
}
