// DTOs mirroring the backend; money fields are strings (backend Decimal) to avoid float rounding.
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  is_admin: boolean;
}

export interface Country {
  code: string;
  name: string;
}

export interface ImportResult {
  inserted: number;
  message: string;
}

export interface ApiErrorDetail {
  field: string;
  message: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: ApiErrorDetail[];
  };
}

export interface UserSummary {
  id: number;
  username: string;
  is_admin: boolean;
  has_all_countries: boolean;
  countries: string[];
}

export interface Product {
  id: number;
  title: string;
  description: string;
  price: string;
  location: string;
}

export interface Page<T> {
  items: T[];
  page: number;
  size: number;
  total_items: number;
  total_pages: number;
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_title: string;
  location: string;
  unit_price: string;
  quantity: number;
  line_total: string;
}

export interface Order {
  id: number;
  order_number: string;
  total_amount: string;
  status: string;
  created_at: string;
  items: OrderItem[];
}
