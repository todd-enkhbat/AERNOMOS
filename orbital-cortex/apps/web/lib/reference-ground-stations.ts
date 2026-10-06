import stations from "../../../simulator/ground_stations.json";

import type { GroundStation } from "@/lib/types";

/** Pinned public-coordinate snapshot bundled with the simulator and API seed. */
export const REFERENCE_GROUND_STATIONS = stations as GroundStation[];
