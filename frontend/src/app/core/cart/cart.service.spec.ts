import { TestBed } from '@angular/core/testing';
import { CartService } from './cart.service';
import { Product } from '../models/api.models';

function product(id: number, price = '10.00'): Product {
  return { id, title: `Item ${id}`, description: 'desc', price, location: 'JO' };
}

describe('CartService', () => {
  let cart: CartService;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({});
    cart = TestBed.inject(CartService);
  });

  it('starts empty', () => {
    expect(cart.count()).toBe(0);
    expect(cart.total()).toBe(0);
  });

  it('adds a product and dedupes repeats (one of each)', () => {
    cart.add(product(1));
    cart.add(product(1));
    expect(cart.count()).toBe(1);
  });

  it('computes the total across items', () => {
    cart.add(product(1, '10.00'));
    cart.add(product(2, '5.50'));
    expect(cart.total()).toBe(15.5);
  });

  it('has() reflects membership', () => {
    cart.add(product(1));
    expect(cart.has(1)).toBeTrue();
    expect(cart.has(2)).toBeFalse();
  });

  it('removes and clears', () => {
    cart.add(product(1));
    cart.add(product(2));
    cart.remove(1);
    expect(cart.count()).toBe(1);
    cart.clear();
    expect(cart.count()).toBe(0);
  });

  it('builds the checkout payload from product ids', () => {
    cart.add(product(3));
    cart.add(product(7));
    expect(cart.toPurchasePayload()).toEqual([{ product_id: 3 }, { product_id: 7 }]);
  });

  it('persists to sessionStorage and reloads', () => {
    cart.add(product(9));
    const reloaded = TestBed.inject(CartService);
    expect(reloaded.has(9)).toBeTrue();
  });
});
