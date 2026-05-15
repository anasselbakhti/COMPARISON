export interface Product {
  id: number;
  name: string;
  brand: string;
  price: string | number;
  category: string;
  source_url?: string;
  specs?: {
    os?: string;
    ram_gb?: number;
    storage_gb?: number;
    camera_mp?: number;
    battery_mah?: number;
    screen_in?: number;
    network?: string;
    cpu?: string;
    gpu?: string;
    battery_wh?: number;
    weight_kg?: number;
    release_year?: number;
    year_release?: number;
  };
  avg_rating?: number;
  updated_at?: string;
}
