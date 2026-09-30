import apiRequest from './apiRequest';
import { makeClaimQualityCheckURL } from './util';

// The advisory, LLM-backed check of a claimed name and address
// (OSDEV-3489), shared by the claim form's Business step and the
// claimed-details form. The backend returns the same
// `warnings: [{type, title, message}]` shape as the SLC quality check.

// Same comparison the backend makes before deciding whether to call the
// model: case-insensitive, with whitespace collapsed.
const normalize = value =>
    (value ?? '').toString().replace(/\s+/g, ' ').trim().toLowerCase();

// Whether the claimant's name and address are the ones in `baseline`
// (the location's current listing on the claim form, the values the
// form loaded on the claimed-details form). Nothing new is asserted for
// an unchanged pair, so there is nothing to check.
export const nameAddressUnchanged = (values, baseline) =>
    normalize(values.name) === normalize(baseline?.name) &&
    normalize(values.address) === normalize(baseline?.address);

// Resolves to the warnings for the pair, or to [] on any failure: the
// check is advisory and fails open on the backend too, so a network
// error or a 5xx must never stop the claimant.
export const fetchClaimQualityWarnings = (osID, { name, address }) =>
    apiRequest
        .post(makeClaimQualityCheckURL(osID), {
            facility_name_english: name ?? '',
            facility_address: address ?? '',
        })
        .then(({ data }) =>
            Array.isArray(data?.warnings) ? data.warnings : [],
        )
        .catch(() => []);

// What a write reports back as `dismissed_warnings`: the type and the
// reason the claimant was shown. The title is looked up server side.
export const toDismissedWarnings = warnings =>
    warnings.map(({ type, message }) => ({ type, message: message ?? '' }));

// The dismissal a form stores alongside the values it was granted for,
// kept as entered; dismissedWarningsFor normalizes when comparing.
export const makeDismissal = (values, warnings) => ({
    name: (values.name ?? '').toString().trim(),
    address: (values.address ?? '').toString().trim(),
    warnings: toDismissedWarnings(warnings),
});

// The warnings to report on a write, or [] when nothing was dismissed
// or the claimant changed the name or address after dismissing (in
// which case the check ran, or will run, again on the new values).
export const dismissedWarningsFor = (values, dismissal) =>
    dismissal && nameAddressUnchanged(values, dismissal)
        ? dismissal.warnings
        : [];
