import { Injectable, computed, signal } from '@angular/core';
import { Product } from '../models/api.models';

const STORAGE_KEY = 'game_store_cart';

@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly products = signal<Product[]>(this.load());

  readonly items = this.products.asReadonly();
  readonly count = computed(() => this.products().length);
  readonly total = computed(() =>
    this.products().reduce((sum, p) => sum + Number(p.price), 0),
  );

  add(product: Product): void {
    this.products.update((list) =>
      list.some((p) => p.id === product.id) ? list : [...list, product],
    );
    this.persist();
  }

  has(productId: number): boolean {
    return this.products().some((p) => p.id === productId);
  }

  remove(productId: number): void {
    this.products.update((list) => list.filter((p) => p.id !== productId));
    this.persist();
  }

  clear(): void {
    this.products.set([]);
    this.persist();
  }

  toPurchasePayload(): { product_id: number }[] {
    return this.products().map((p) => ({ product_id: p.id }));
  }

  private persist(): void {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(this.products()));
    } catch {

    }
  }

  private load(): Product[] {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as Product[]) : [];
    } catch {
      return [];
    }
  }
}
