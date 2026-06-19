# TrustPay API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## Authentication

All protected endpoints require `Authorization: Bearer <access_token>` header.

## Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout |

### Users
| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Get current user |
| PATCH | `/users/me` | Update current user |
| POST | `/users/me/change-password` | Change password |

### KYC
| Method | Path | Description |
|--------|------|-------------|
| POST | `/kyc/start` | Start KYC request |
| POST | `/kyc/{id}/step1` | Submit personal info |
| POST | `/kyc/{id}/documents` | Upload document |
| POST | `/kyc/{id}/submit` | Final submission |
| GET | `/kyc/my-requests` | List my KYC requests |

### Wallet
| Method | Path | Description |
|--------|------|-------------|
| GET | `/wallet/` | Get wallet info |
| GET | `/wallet/transactions` | List transactions |

### Admin
| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/dashboard` | Dashboard stats |
| GET | `/admin/users` | List all users |
| GET | `/admin/kyc` | List KYC requests |
| POST | `/admin/kyc/{id}/review` | Review KYC |

### Analytics
| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/overview` | Platform overview metrics |
