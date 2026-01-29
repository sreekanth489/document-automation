import React from 'react';
import { PassportData, G28Data } from '../api/client';

interface DataFieldProps {
  label: string;
  value: string | null;
  onChange: (value: string) => void;
}

function DataField({ label, value, onChange }: DataFieldProps) {
  return (
    <div className="data-field">
      <label>{label}</label>
      <input
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

interface ExtractedDataDisplayProps {
  passport: PassportData | null;
  g28: G28Data | null;
  onPassportChange: (data: PassportData) => void;
  onG28Change: (data: G28Data) => void;
}

export function ExtractedDataDisplay({
  passport,
  g28,
  onPassportChange,
  onG28Change,
}: ExtractedDataDisplayProps) {
  const updatePassport = (field: keyof PassportData, value: string) => {
    if (passport) {
      onPassportChange({ ...passport, [field]: value || null });
    }
  };

  const updateG28 = (field: keyof G28Data, value: string) => {
    if (g28) {
      onG28Change({ ...g28, [field]: value || null });
    }
  };

  return (
    <div className="card">
      <h2>Extracted Data</h2>
      <p style={{ marginBottom: '1rem', color: '#666' }}>
        Review and edit the extracted data before filling the form.
      </p>

      {passport && (
        <>
          <div className="section-title">Passport Information (Beneficiary)</div>
          <div className="data-grid">
            <DataField
              label="Last Name"
              value={passport.last_name}
              onChange={(v) => updatePassport('last_name', v)}
            />
            <DataField
              label="First Name(s)"
              value={passport.first_name}
              onChange={(v) => updatePassport('first_name', v)}
            />
            <DataField
              label="Middle Name(s)"
              value={passport.middle_name}
              onChange={(v) => updatePassport('middle_name', v)}
            />
            <DataField
              label="Passport Number"
              value={passport.passport_number}
              onChange={(v) => updatePassport('passport_number', v)}
            />
            <DataField
              label="Country of Issue"
              value={passport.country_of_issue}
              onChange={(v) => updatePassport('country_of_issue', v)}
            />
            <DataField
              label="Nationality"
              value={passport.nationality}
              onChange={(v) => updatePassport('nationality', v)}
            />
            <DataField
              label="Date of Birth"
              value={passport.date_of_birth}
              onChange={(v) => updatePassport('date_of_birth', v)}
            />
            <DataField
              label="Place of Birth"
              value={passport.place_of_birth}
              onChange={(v) => updatePassport('place_of_birth', v)}
            />
            <DataField
              label="Sex"
              value={passport.sex}
              onChange={(v) => updatePassport('sex', v)}
            />
            <DataField
              label="Date of Issue"
              value={passport.date_of_issue}
              onChange={(v) => updatePassport('date_of_issue', v)}
            />
            <DataField
              label="Date of Expiration"
              value={passport.date_of_expiration}
              onChange={(v) => updatePassport('date_of_expiration', v)}
            />
          </div>
        </>
      )}

      {g28 && (
        <>
          <div className={passport ? 'section-divider' : ''}>
            <div className="section-title">Attorney Information (G-28)</div>
          </div>
          <div className="data-grid">
            <DataField
              label="Family Name"
              value={g28.attorney_family_name}
              onChange={(v) => updateG28('attorney_family_name', v)}
            />
            <DataField
              label="Given Name"
              value={g28.attorney_given_name}
              onChange={(v) => updateG28('attorney_given_name', v)}
            />
            <DataField
              label="Middle Name"
              value={g28.attorney_middle_name}
              onChange={(v) => updateG28('attorney_middle_name', v)}
            />
            <DataField
              label="Street Address"
              value={g28.street_address}
              onChange={(v) => updateG28('street_address', v)}
            />
            <DataField
              label="City"
              value={g28.city}
              onChange={(v) => updateG28('city', v)}
            />
            <DataField
              label="State"
              value={g28.state}
              onChange={(v) => updateG28('state', v)}
            />
            <DataField
              label="ZIP Code"
              value={g28.zip_code}
              onChange={(v) => updateG28('zip_code', v)}
            />
            <DataField
              label="Country"
              value={g28.country}
              onChange={(v) => updateG28('country', v)}
            />
            <DataField
              label="Daytime Phone"
              value={g28.daytime_phone}
              onChange={(v) => updateG28('daytime_phone', v)}
            />
            <DataField
              label="Mobile Phone"
              value={g28.mobile_phone}
              onChange={(v) => updateG28('mobile_phone', v)}
            />
            <DataField
              label="Email"
              value={g28.email}
              onChange={(v) => updateG28('email', v)}
            />
            <DataField
              label="Licensing Authority"
              value={g28.licensing_authority}
              onChange={(v) => updateG28('licensing_authority', v)}
            />
            <DataField
              label="Bar Number"
              value={g28.bar_number}
              onChange={(v) => updateG28('bar_number', v)}
            />
            <DataField
              label="Law Firm Name"
              value={g28.law_firm_name}
              onChange={(v) => updateG28('law_firm_name', v)}
            />
          </div>
        </>
      )}
    </div>
  );
}
