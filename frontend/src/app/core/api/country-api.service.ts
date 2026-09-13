import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Country } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class CountryApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/countries`;

  list(): Observable<Country[]> {
    return this.http.get<Country[]>(this.baseUrl);
  }

  create(code: string, name: string): Observable<Country> {
    return this.http.post<Country>(this.baseUrl, { code, name });
  }
}
