import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { OrderApiService } from '../../core/api/order-api.service';
import { CartService } from '../../core/cart/cart.service';

@Component({
  selector: 'app-cart-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './cart-page.html',
  styleUrl: './cart-page.scss',
})
export class CartPage {
  readonly cart = inject(CartService);
  private readonly orderApi = inject(OrderApiService);
  private readonly router = inject(Router);

  readonly placing = signal(false);
  readonly error = signal<string | null>(null);
  readonly isEmpty = computed(() => this.cart.items().length === 0);

  checkout(): void {
    if (this.isEmpty() || this.placing()) {
      return;
    }
    this.placing.set(true);
    this.error.set(null);
    this.orderApi.checkout(this.cart.toPurchasePayload()).subscribe({
      next: (order) => {
        this.cart.clear();
        this.router.navigate(['/orders', order.id]);
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(err.error?.error?.message ?? 'Checkout failed. Please try again.');
        this.placing.set(false);
      },
    });
  }
}
