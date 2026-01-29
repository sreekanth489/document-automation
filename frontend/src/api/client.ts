import axios from 'axios';

const API_BASE = '/api';

export interface PassportData {
  last_name: string | null;
  first_name: string | null;
  middle_name: string | null;
  passport_number: string | null;
  country_of_issue: string | null;
  nationality: string | null;
  date_of_birth: string | null;
  place_of_birth: string | null;
  sex: string | null;
  date_of_issue: string | null;
  date_of_expiration: string | null;
}

export interface G28Data {
  attorney_family_name: string | null;
  attorney_given_name: string | null;
  attorney_middle_name: string | null;
  street_address: string | null;
  apt_ste_flr: string | null;
  apt_ste_flr_number: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  country: string | null;
  daytime_phone: string | null;
  mobile_phone: string | null;
  email: string | null;
  licensing_authority: string | null;
  bar_number: string | null;
  law_firm_name: string | null;
}

export interface ExtractedData {
  session_id: string;
  passport: PassportData | null;
  g28: G28Data | null;
}

export interface FormFillResponse {
  success: boolean;
  message: string;
  screenshot_path: string | null;
}

export async function uploadDocuments(
  passportFile: File | null,
  g28File: File | null
): Promise<ExtractedData> {
  const formData = new FormData();

  if (passportFile) {
    formData.append('passport', passportFile);
  }
  if (g28File) {
    formData.append('g28', g28File);
  }

  const response = await axios.post<ExtractedData>(
    `${API_BASE}/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
}

export async function fillForm(
  sessionId: string,
  passport: PassportData | null,
  g28: G28Data | null,
  headless: boolean = false
): Promise<FormFillResponse> {
  const response = await axios.post<FormFillResponse>(`${API_BASE}/fill-form`, {
    session_id: sessionId,
    passport,
    g28,
    headless,
  });

  return response.data;
}
