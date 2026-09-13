import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { OrderApiService } from '../../core/api/order-api.service';
import { ProductApiService } from '../../core/api/product-api.service';
import { CartService } from '../../core/cart/cart.service';
import { Product } from '../../core/models/api.models';

@Component({
  selector: 'app-product-details-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './product-details-page.html',
  styleUrl: './product-details-page.scss',
})
export class ProductDetailsPage implements OnInit {
  private readonly productApi = inject(ProductApiService);
  private readonly orderApi = inject(OrderApiService);
  readonly cart = inject(CartService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly product = signal<Product | null>(null);
  readonly error = signal<string | null>(null);
  readonly buying = signal(false);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.productApi.getById(id).subscribe({
      next: (product) => this.product.set(product),
      error: (err: HttpErrorResponse) =>
        this.error.set(err.status === 404 ? 'Product not found.' : 'Could not load this product.'),
    });
  }

  addToCart(): void {
    const product = this.product();
    if (product) {
      this.cart.add(product);
    }
  }

  buyNow(): void {
    const product = this.product();
    if (!product || this.buying()) {
      return;
    }
    this.buying.set(true);
    this.orderApi.checkout([{ product_id: product.id }]).subscribe({
      next: (order) => this.router.navigate(['/orders', order.id]),
      error: (err: HttpErrorResponse) => {
        this.error.set(err.error?.error?.message ?? 'Purchase failed. Please try again.');
        this.buying.set(false);
      },
    });
  }
}
