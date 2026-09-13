import { Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, map, of, switchMap, tap } from 'rxjs';
import { CountryApiService } from '../../core/api/country-api.service';
import { ProductApiService } from '../../core/api/product-api.service';
import { CartService } from '../../core/cart/cart.service';
import { Country, Page, Product } from '../../core/models/api.models';

@Component({
  selector: 'app-product-list-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './product-list-page.html',
  styleUrl: './product-list-page.scss',
})
export class ProductListPage {
  private readonly api = inject(ProductApiService);
  private readonly countryApi = inject(CountryApiService);
  readonly cart = inject(CartService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly pageSize = 12;
  readonly result = signal<Page<Product> | null>(null);
  readonly location = signal<string | null>(null);
  readonly countries = signal<Country[]>([]);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  constructor() {
    this.countryApi.list().subscribe((c) => this.countries.set(c));

    this.route.queryParamMap
      .pipe(
        map((params) => ({
          page: Number(params.get('page')) || 1,
          location: params.get('location'),
        })),
        tap((query) => {
          this.location.set(query.location);
          this.loading.set(true);
          this.error.set(null);
        }),
        switchMap((query) =>
          this.api.list(query.page, this.pageSize, query.location).pipe(
            catchError(() => {
              this.error.set('Could not load products. Please try again.');
              return of(null);
            }),
          ),
        ),
        takeUntilDestroyed(),
      )
      .subscribe((page) => {
        this.result.set(page);
        this.loading.set(false);
      });
  }

  goToPage(page: number): void {
    this.router.navigate([], { queryParams: { page }, queryParamsHandling: 'merge' });
  }

  filterBy(location: string | null): void {
    this.router.navigate([], { queryParams: { location, page: 1 }, queryParamsHandling: 'merge' });
  }

  toggleCart(product: Product): void {
    if (this.cart.has(product.id)) {
      this.cart.remove(product.id);
    } else {
      this.cart.add(product);
    }
  }
}
