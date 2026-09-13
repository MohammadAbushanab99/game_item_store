import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ImportResult, Product, UserSummary } from '../models/api.models';

export interface NewProduct {
  title: string;
  description: string;
  price: string;
  location: string;
  id?: number;
}

export interface UserAccessUpdate {
  has_all_countries: boolean;
  countries: string[];
}

@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/products`;
  private readonly adminUrl = `${environment.apiUrl}/admin`;

  createProduct(product: NewProduct): Observable<Product> {
    return this.http.post<Product>(this.baseUrl, product);
  }

  importFile(file: File): Observable<ImportResult> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<ImportResult>(`${this.baseUrl}/import`, form);
  }

  getUsers(): Observable<UserSummary[]> {
    return this.http.get<UserSummary[]>(`${this.adminUrl}/users`);
  }

  updateUserAccess(userId: number, update: UserAccessUpdate): Observable<UserSummary> {
    return this.http.put<UserSummary>(`${this.adminUrl}/users/${userId}/access`, update);
  }
}
