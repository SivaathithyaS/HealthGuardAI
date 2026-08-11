# API contract (draft — finalize between Backend + Frontend before building forms)

## Auth
- POST /auth/register
- POST /auth/login → { access_token }

## Prediction
- POST /predict/{disease}
  body: { features: { ... } }
  returns: { risk_score, risk_label, shap_values, top_factors }

## Roadmap
- POST /roadmap/{disease}
  body: { features: {...}, shap_values: {...} }
  returns: { what_if: [...], goals: { short_term, medium_term, long_term } }

## OCR
- POST /ocr/upload  (multipart file)
  returns: { extracted_features: {...} }
  Note: frontend shows these pre-filled in the prediction form for user
  confirmation before calling /predict — not submitted automatically.

## Reports
- GET /reports/{prediction_id}/pdf
  returns: PDF file

## History / Dashboard
- GET /history/{user_id}
  returns: list of past predictions for trend charts
