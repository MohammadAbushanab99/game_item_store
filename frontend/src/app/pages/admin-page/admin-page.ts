import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AdminApiService } from '../../core/api/admin-api.service';
import { CountryApiService } from '../../core/api/country-api.service';
import { ApiError, ApiErrorDetail, Country, UserSummary } from '../../core/models/api.models';

interface EditableUser extends UserSummary {
  saving: boolean;
  savedMessage: string | null;
}

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './admin-page.html',
  styleUrl: './admin-page.scss',
})
export class AdminPage implements OnInit {
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly countryApi = inject(CountryApiService);
  private readonly adminApi = inject(AdminApiService);

  readonly activeTab = signal<'catalogue' | 'access'>('catalogue');

  readonly countries = signal<Country[]>([]);

  readonly countryForm = this.fb.group({
    code: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(3)]],
    name: ['', [Validators.required]],
  });
  readonly countryMsg = signal<string | null>(null);
  readonly countryErr = signal<string | null>(null);

  readonly productForm = this.fb.group({
    title: ['', [Validators.required]],
    description: ['', [Validators.required]],
    price: ['', [Validators.required, Validators.pattern(/^\d+(\.\d{1,2})?$/)]],
    location: ['', [Validators.required]],
  });
  readonly productMsg = signal<string | null>(null);
  readonly productErr = signal<string | null>(null);

  readonly selectedFileName = signal<string | null>(null);
  private selectedFile: File | null = null;
  readonly importing = signal(false);
  readonly importMsg = signal<string | null>(null);
  readonly importGeneralError = signal<string | null>(null);
  readonly importRowErrors = signal<ApiErrorDetail[]>([]);

  readonly users = signal<EditableUser[]>([]);
  readonly usersError = signal<string | null>(null);

  ngOnInit(): void {
    this.loadCountries();
    this.loadUsers();
  }

  private loadCountries(): void {
    this.countryApi.list().subscribe((c) => this.countries.set(c));
  }

  private loadUsers(): void {
    this.adminApi.getUsers().subscribe({
      next: (list) =>
        this.users.set(list.map((u) => ({ ...u, countries: [...u.countries], saving: false, savedMessage: null }))),
      error: (err: HttpErrorResponse) => this.usersError.set(this.messageOf(err, 'Could not load users.')),
    });
  }

  private patchUser(id: number, changes: Partial<EditableUser>): void {
    this.users.update((list) => list.map((u) => (u.id === id ? { ...u, ...changes } : u)));
  }

  setAllCountries(user: EditableUser, checked: boolean): void {
    this.patchUser(user.id, { has_all_countries: checked, savedMessage: null });
  }

  toggleCountry(user: EditableUser, code: string, checked: boolean): void {
    const codes = checked
      ? [...user.countries, code]
      : user.countries.filter((c) => c !== code);
    this.patchUser(user.id, { countries: codes, savedMessage: null });
  }

  saveUser(user: EditableUser): void {
    this.patchUser(user.id, { saving: true, savedMessage: null });
    this.adminApi
      .updateUserAccess(user.id, { has_all_countries: user.has_all_countries, countries: user.countries })
      .subscribe({
        next: (updated) =>
          this.patchUser(user.id, {
            countries: [...updated.countries],
            has_all_countries: updated.has_all_countries,
            saving: false,
            savedMessage: 'Saved.',
          }),
        error: (err: HttpErrorResponse) =>
          this.patchUser(user.id, { saving: false, savedMessage: this.messageOf(err, 'Save failed.') }),
      });
  }

  addCountry(): void {
    this.countryMsg.set(null);
    this.countryErr.set(null);
    if (this.countryForm.invalid) {
      this.countryForm.markAllAsTouched();
      return;
    }
    const { code, name } = this.countryForm.getRawValue();
    this.countryApi.create(code, name).subscribe({
      next: (country) => {
        this.countryMsg.set(`Added ${country.name} (${country.code}).`);
        this.countryForm.reset();
        this.loadCountries();
      },
      error: (err: HttpErrorResponse) => this.countryErr.set(this.messageOf(err, 'Could not add country.')),
    });
  }

  addProduct(): void {
    this.productMsg.set(null);
    this.productErr.set(null);
    if (this.productForm.invalid) {
      this.productForm.markAllAsTouched();
      return;
    }
    this.adminApi.createProduct(this.productForm.getRawValue()).subscribe({
      next: (product) => {
        this.productMsg.set(`Added "${product.title}" (id ${product.id}).`);
        this.productForm.reset();
      },
      error: (err: HttpErrorResponse) => this.productErr.set(this.messageOf(err, 'Could not add product.')),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
    this.selectedFileName.set(this.selectedFile?.name ?? null);
    this.importMsg.set(null);
    this.importGeneralError.set(null);
    this.importRowErrors.set([]);
  }

  runImport(): void {
    if (!this.selectedFile || this.importing()) {
      return;
    }
    this.importing.set(true);
    this.importMsg.set(null);
    this.importGeneralError.set(null);
    this.importRowErrors.set([]);

    this.adminApi.importFile(this.selectedFile).subscribe({
      next: (result) => {
        this.importMsg.set(result.message);
        this.importing.set(false);
      },
      error: (err: HttpErrorResponse) => {
        const body = err.error as ApiError | undefined;
        const details = body?.error?.details ?? [];
        if (details.length > 0) {
          this.importRowErrors.set(details);
          this.importGeneralError.set(body?.error?.message ?? 'Import failed.');
        } else {
          this.importGeneralError.set(body?.error?.message ?? 'Import failed. Please check the file.');
        }
        this.importing.set(false);
      },
    });
  }

  private messageOf(err: HttpErrorResponse, fallback: string): string {
    return (err.error as ApiError | undefined)?.error?.message ?? fallback;
  }
}
