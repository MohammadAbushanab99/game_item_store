import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { OrderApiService } from '../../core/api/order-api.service';
import { Order } from '../../core/models/api.models';

@Component({
  selector: 'app-receipt-page',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './receipt-page.html',
  styleUrl: './receipt-page.scss',
})
export class ReceiptPage implements OnInit {
  private readonly orderApi = inject(OrderApiService);
  private readonly route = inject(ActivatedRoute);

  readonly order = signal<Order | null>(null);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {

    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.orderApi.getById(id).subscribe({
      next: (order) => this.order.set(order),
      error: () => this.error.set('Order not found.'),
    });
  }

  print(): void {
    window.print();
  }
}
