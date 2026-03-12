import React from 'react';
import moment from 'moment';
import orderBy from 'lodash/orderBy';
import identity from 'lodash/identity';

import ENERGY_SOURCE_UNITS from './constants';
import renderUniqueListItems from '../../util/renderUtils';
import { addProtocolToWebsiteURLIfMissing } from '../../util/util';

/**
 * Format energy source name from snake_case to Title Case.
 */
export const formatEnergySourceName = key =>
    key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

/**
 * Pluralize unit based on value.
 */
export const pluralizeUnit = (unit, value) => {
    // Special cases that don't pluralize.
    if (value === 1) return unit;
    if (unit === 'MWh') return unit;

    return `${unit}s`;
};

/**
 * Format actual annual energy consumption data into readable strings.
 */
export const formatEnergyConsumption = energyData => {
    if (!energyData) return null;

    const entries = Object.entries(energyData)
        .filter(([, value]) => value !== null && value !== undefined)
        .map(([key, value]) => {
            const unit = ENERGY_SOURCE_UNITS[key] || 'Joule';
            const formattedName = formatEnergySourceName(key);
            const pluralizedUnit = pluralizeUnit(unit, value);
            return `${formattedName}: ${value} ${pluralizedUnit}`;
        });

    return entries.length > 0 ? entries : null;
};

/**
 * Check if value is valid for display (handles both strings and React
 * elements).
 */
export const hasDisplayableValue = value => {
    if (!value) return false;

    // Handle string values.
    if (typeof value === 'string') {
        return value.trim().length > 0;
    }

    // Handle React elements (JSX).
    if (React.isValidElement(value)) {
        return true;
    }

    // Handle arrays (like from renderUniqueListItems).
    if (Array.isArray(value)) {
        return value.length > 0;
    }

    // Handle other truthy values (numbers, objects, etc.).
    return true;
};

/**
 * Configuration for location claim information fields.
 * Each field defines:
 * - key: unique identifier
 * - label: display label
 * - getValue: function to extract/format value from location data
 * - fullWidth: whether field should take full width (optional)
 */
export const getLocationFieldsConfig = (location, contact, office) => [
    // Location website.
    {
        key: 'website',
        label: 'Website',
        tooltipText:
            'Official website URL for this specific production location.',
        getValue: () =>
            location.website ? (
                <a
                    href={addProtocolToWebsiteURLIfMissing(location.website)}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    {location.website}
                </a>
            ) : null,
    },
    // Contact fields (only if contact exists).
    ...(contact
        ? [
              {
                  key: 'contact_name',
                  label: 'Contact Person',
                  getValue: () => contact.name,
              },
              {
                  key: 'contact_email',
                  label: 'Contact Email',
                  getValue: () => contact.email,
              },
          ]
        : []),
    // Location fields.
    {
        key: 'phone_number',
        label: 'Phone Number',
        tooltipText:
            'Main phone number for contacting this production location directly.',
        getValue: () => location.phone_number,
    },
    {
        key: 'minimum_order',
        label: 'Minimum Order',
        tooltipText:
            'Smallest order quantity this production location will accept from customers.',
        getValue: () => location.minimum_order,
    },
    {
        key: 'average_lead_time',
        label: 'Average Lead Time',
        tooltipText:
            'Typical time required from order confirmation to product delivery.',
        getValue: () => location.average_lead_time,
    },
    {
        key: 'female_workers_percentage',
        label: 'Percentage of female workers',
        tooltipText:
            'Percentage of female employees out of the total workforce at this location.',
        getValue: () => location.female_workers_percentage,
    },
    {
        key: 'affiliations',
        label: 'Affiliations',
        tooltipText:
            'Industry associations and partner entities as declared by the production location. OS Hub does not independently verify this information.',
        getValue: () =>
            location.affiliations && location.affiliations.length
                ? renderUniqueListItems(
                      orderBy(location.affiliations, identity),
                  )
                : null,
    },
    {
        key: 'certifications',
        label: 'Certifications/Standards/Regulations',
        tooltipText:
            'Certifications and standards the production location self-reports as adhering to. OS Hub does not verify this information.',
        getValue: () =>
            location.certifications && location.certifications.length
                ? renderUniqueListItems(
                      orderBy(location.certifications, identity),
                  )
                : null,
    },
    {
        key: 'opening_date',
        label: 'Opening Date',
        getValue: () => location.opening_date || null,
    },
    {
        key: 'closing_date',
        label: 'Closing Date',
        getValue: () =>
            location.closing_date
                ? moment(location.closing_date, 'YYYY-MM').format('MMMM YYYY')
                : null,
    },
    {
        key: 'estimated_annual_throughput',
        label: 'Estimated Annual Throughput',
        tooltipText:
            'Total amount of materials or products processed by this location per year.',
        getValue: () =>
            location.estimated_annual_throughput
                ? `${location.estimated_annual_throughput} kg/year`
                : null,
    },
    {
        key: 'actual_annual_energy_consumption',
        label: 'Actual Annual Energy Consumption',
        tooltipText:
            'Annual energy consumption by source reported by this production location.',
        getValue: () => {
            const formattedData = formatEnergyConsumption(
                location.actual_annual_energy_consumption,
            );
            return formattedData ? renderUniqueListItems(formattedData) : null;
        },
    },
    // Office fields (only if office exists).
    ...(office
        ? [
              {
                  key: 'office_name',
                  label: 'Office Name',
                  tooltipText: 'Name of the corporate office or headquarters.',
                  getValue: () => office.name,
              },
              {
                  key: 'office_address',
                  label: 'Office Address',
                  tooltipText: 'Physical address of the office location.',
                  getValue: () =>
                      `${office.address || ' '} ${office.country || ' '}`,
              },
              {
                  key: 'office_phone_number',
                  label: 'Office Phone Number',
                  getValue: () => office.phone_number,
              },
          ]
        : []),
    // Description (full width, last).
    {
        key: 'description',
        label: 'Description',
        fullWidth: true,
        tooltipText:
            'A brief overview of what this production location manufactures and its main business activities.',
        getValue: () => location.description,
    },
];
