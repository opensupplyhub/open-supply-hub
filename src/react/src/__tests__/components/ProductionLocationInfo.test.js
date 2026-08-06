import React from "react";
import { fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, BrowserRouter as Router } from "react-router-dom";

import ProductionLocationInfo from "../../components/Contribute/ProductionLocationInfo";
import renderWithProviders from "../../util/testUtils/renderWithProviders";
import { MAINTENANCE_MESSAGE } from "../../util/constants";
import apiRequest from "../../util/apiRequest";

beforeAll(() => {
    window.scrollTo = jest.fn();
});

jest.mock('@material-ui/core/Popper', () => ({ children }) => children);
jest.mock('@material-ui/core/Portal', () => ({ children }) => children);

jest.mock("../../util/apiRequest", () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
        post: jest.fn(),
        patch: jest.fn(),
    },
}));

// CRA's jest config sets `resetMocks: true`, which strips any implementation
// given to jest.fn() before every test, so the mocked resolved values must be
// (re)assigned here rather than in the jest.mock factory above.
beforeEach(() => {
    apiRequest.get.mockResolvedValue({ data: [] });
    apiRequest.post.mockResolvedValue({ data: {} });
    apiRequest.patch.mockResolvedValue({ data: {} });
});

jest.mock("../../components/Filters/StyledSelect", () => (props) => {
    const { options = [], value, onChange, onBlur, placeholder, name } = props;

    return (
        <select
            data-testid={`mocked-select-${name}`}
            value={value ? value.value : ""}
            onChange={(e) => {
                const selectedOption = options.find(
                    (opt) => opt.value === e.target.value,
                );
                onChange(
                    name === 'country' ? selectedOption : [selectedOption]
                );
            }}
            onBlur={onBlur}
        >
            <option value="">{placeholder}</option>
            {options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                    {opt.label}
                </option>
            ))}
        </select>
    );
});

describe("ProductionLocationInfo component, test input fields for POST v1/production-locations", () => {
    const defaultState = {
        filterOptions: {
            countries: {
                data: [{ value: "US", label: "United States" }],
                error: null,
                fetching: false,
            },
            facilityProcessingType: {
                data: [],
                error: null,
                fetching: false,
            },
        },
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
        featureFlags: {
            flags: {
                disable_list_uploading: false,
            },
            fetching: false,
        }

    };

    const defaultProps = {
        submitMethod: "POST",
    };

    const renderComponent = (props = {}, preloadedState = defaultState) =>
        renderWithProviders(
            <Router>
                <ProductionLocationInfo {...defaultProps} {...props} />
            </Router>,
            { preloadedState },
        );

    test("renders the production location form", () => {
        const { getByText, getByPlaceholderText, getAllByText, getByTestId } = renderComponent();

        expect(getByText("Production Location Information")).toBeInTheDocument();
        expect(getByText("Use the form below to edit the name, address, and country for your production location.")).toBeInTheDocument();
        expect(getByText("Location Name")).toBeInTheDocument();
        expect(getByText("Enter the name of the production location that you are uploading.")).toBeInTheDocument();
        expect(getByText("Address")).toBeInTheDocument();
        expect(getByText("Enter the address of the production location. We will use this to plot the location on a map.")).toBeInTheDocument();
        expect(getAllByText("Country")).toHaveLength(2);
        expect(getByText("Select the country where the production site is located.")).toBeInTheDocument();
        expect(getByText("Additional information")).toBeInTheDocument();
        expect(
            getByText("Expand this section to add more data about your production location, including product types, number of workers, parent company and more."),
        ).toBeInTheDocument();

        const nameInput = getByPlaceholderText("Enter the name");
        expect(nameInput).toBeInTheDocument();
        expect(nameInput).toHaveValue("");

        const addressInput = getByPlaceholderText("Enter the full address");
        expect(addressInput).toBeInTheDocument();
        expect(addressInput).toHaveValue("");

        const countrySelect = getByTestId("mocked-select-country");
        expect(countrySelect).toBeInTheDocument();
        expect(countrySelect).toHaveValue("");

        const switchButton = getByTestId("switch-additional-info-fields");
        expect(switchButton).toBeInTheDocument();
    });

    test("displays error (and disables submit) when required fields are empty after blur", async () => {
        const { getByRole, getByPlaceholderText, getAllByText, getByTestId } = renderComponent();

        const submitButton = getByRole("button", { name: /Submit/i });
        await waitFor(() => expect(submitButton).toBeDisabled());

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select-country");

        fireEvent.blur(nameInput);
        fireEvent.blur(addressInput);
        fireEvent.blur(countrySelect);

        const nameError = getAllByText("Name is required.");
        const addressError = getAllByText("Address is required.");
        const countryError = getAllByText("Country is required.");
        expect(nameError).toHaveLength(1);
        expect(addressError).toHaveLength(1);
        expect(countryError).toHaveLength(1);
        

        expect(getByPlaceholderText("Enter the name")).toHaveAttribute("aria-invalid", "true");
        expect(getByPlaceholderText("Enter the full address")).toHaveAttribute("aria-invalid", "true");
    });

    test("enables the submit button when required fields are filled", async () => {
        const { getByRole, getByPlaceholderText, getByTestId } = renderComponent();

        const submitButton = getByRole("button", { name: /Submit/i });
        await waitFor(() => expect(submitButton).toBeDisabled());

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select-country");

        fireEvent.change(nameInput, { target: { value: "Test Name" } });
        fireEvent.change(addressInput, { target: { value: "Test Address" } });
        fireEvent.change(countrySelect, { target: { value: "US" } });

        expect(countrySelect.value).toBe("US");
        await waitFor(() => expect(submitButton).toBeEnabled());
    });

    test("shows every triggered client-side warning together in one dialog", async () => {
        const { getByRole, getByText, getByPlaceholderText, getByTestId } = renderComponent();

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select-country");

        fireEvent.change(nameInput, { target: { value: "Test Name" } });
        // Short enough to also read as a PO Box, so both client-side
        // address checks fire from a single field value.
        fireEvent.change(addressInput, { target: { value: "PO Box 1" } });
        fireEvent.change(countrySelect, { target: { value: "US" } });

        const submitButton = getByRole("button", { name: /Submit/i });
        await waitFor(() => expect(submitButton).toBeEnabled());
        fireEvent.click(submitButton);

        await waitFor(() =>
            expect(getByText("Please Review Before Submitting")).toBeInTheDocument(),
        );
        expect(getByText("Address May Contain a PO Box")).toBeInTheDocument();
        expect(getByText("Address Appears Short")).toBeInTheDocument();
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test("displays additional information form when icon button is clicked", () => {
        const { getByTestId, getByText, queryByText } = renderComponent();

        const switchButton = getByTestId("switch-additional-info-fields");
        fireEvent.click(switchButton);

        expect(getByText("Sector(s)")).toBeInTheDocument();
        expect(getByText("Select the sector(s) that this location operates in. For example: Apparel, Electronics, Renewable Energy.")).toBeInTheDocument();
        expect(getByText("Product Type(s)")).toBeInTheDocument();
        expect(getByText("Enter the type of products produced at this location. For example: Shirts, Laptops, Solar Panels.")).toBeInTheDocument();
        expect(getByText("Location Type(s)")).toBeInTheDocument();
        expect(getByText("Select or enter the location type(s) for this production location. For example: Final Product Assembly, Raw Materials Production or Processing, Office/HQ.")).toBeInTheDocument();
        expect(getByText("Processing Type(s)")).toBeInTheDocument();
        expect(getByText("Select or enter the type of processing activities that take place at this location. For example: Printing, Tooling, Assembly.")).toBeInTheDocument();
        expect(getByText("Number of Workers")).toBeInTheDocument();
        expect(getByText("Enter a number or a range for the number of people employed at the location. For example: 100, 100-150.")).toBeInTheDocument();
        expect(getByText("Parent Company")).toBeInTheDocument();
        expect(getByText("Enter the company that holds majority ownership for this production.")).toBeInTheDocument();

        fireEvent.click(switchButton);

        expect(queryByText("Sector(s)")).not.toBeInTheDocument();
        expect(queryByText("Product Type(s)")).not.toBeInTheDocument();
        expect(queryByText("Location Type(s)")).not.toBeInTheDocument();
        expect(queryByText("Processing Type(s)")).not.toBeInTheDocument();
        expect(queryByText("Number of Workers")).not.toBeInTheDocument();
        expect(queryByText("Parent Company")).not.toBeInTheDocument();
    });

    test("displays error when number of workers is not a valid number and disable submit button", async () => {
        const { getByRole, getByPlaceholderText, getByTestId } = renderComponent();

        const submitButton = getByRole("button", { name: /Submit/i });
        await waitFor(() => expect(submitButton).toBeDisabled());

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select-country");

        fireEvent.change(nameInput, { target: { value: "Test Name" } });
        fireEvent.change(addressInput, { target: { value: "Test Address" } });
        fireEvent.change(countrySelect, { target: { value: "US" } });

        await waitFor(() => expect(submitButton).toBeEnabled());

        const switchButton = getByTestId("switch-additional-info-fields");
        expect(switchButton).not.toBeChecked();

        fireEvent.click(switchButton);
        expect(switchButton).toBeChecked();

        const numberOfWorkersInput = getByPlaceholderText("Enter the number of workers as a number or range");
        fireEvent.change(numberOfWorkersInput, { target: { value: "Test" } });

        await waitFor(() => 
            expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "true")
        );
        await waitFor(() => expect(submitButton).toBeDisabled());

        fireEvent.change(numberOfWorkersInput, { target: { value: "100" } });

        await waitFor(() => 
            expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "false")
        );
        await waitFor(() => expect(submitButton).toBeEnabled());

        fireEvent.change(numberOfWorkersInput, { target: { value: "100-150" } });
        await waitFor(() => 
            expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "false")
        );
        await waitFor(() => expect(submitButton).toBeEnabled());

        fireEvent.change(numberOfWorkersInput, { target: { value: "200-100" } });

        await waitFor(() => 
            expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "true")
        );
        await waitFor(() => expect(submitButton).toBeDisabled());
    });

    test("update button should be disabled when active feature flags include DISABLE_LIST_UPLOADING", () => {
        const updatedState = {
            ...defaultState,
            featureFlags: {
                ...defaultState.featureFlags,
                flags: {
                    ...defaultState.featureFlags.flags,
                    disable_list_uploading: true,
                },
            },
        };
    
        const { getByRole } = renderComponent({}, updatedState);
        const submitButton = getByRole("button", { name: /Submit/i });
        expect(submitButton).toBeDisabled();
    });

    test("shows tooltip on hover submit button when active feature flags include DISABLE_LIST_UPLOADING", () => {
        const updatedState = {
            ...defaultState,
            featureFlags: {
                ...defaultState.featureFlags,
                flags: {
                    ...defaultState.featureFlags.flags,
                    disable_list_uploading: true,
                },
            },
        };

        const { getByRole } = renderComponent({}, updatedState);
        const submitButton = getByRole("button", { name: /Submit/i });

        expect(submitButton).toBeDisabled();

        const noTooltipElement = document.querySelector(`[title="${MAINTENANCE_MESSAGE}"]`);

        expect(noTooltipElement).toBeInTheDocument();
        fireEvent.mouseOver(submitButton);

        const tooltip = document.querySelector('[aria-describedby^="mui-tooltip-"]');

        expect(tooltip).toBeInTheDocument();
        fireEvent.mouseOut(submitButton);

        const noTooltipElementAfter = document.querySelector(`[title="${MAINTENANCE_MESSAGE}"]`);

        expect(noTooltipElementAfter).toBeInTheDocument();
    });

    test("displays select or input for location and processing type fields", () => {
        const { getByTestId, getByText } = renderComponent();

        const switchButton = getByTestId("switch-additional-info-fields");
        fireEvent.click(switchButton);
    
        expect(getByText("Enter location type(s)")).toBeInTheDocument();
        expect(getByText("Enter processing type(s)")).toBeInTheDocument();

        const sectorSelect = getByTestId("mocked-select-sector");
        fireEvent.change(sectorSelect, { target: { value: 'Apparel' } });

        expect(getByText("Select location type(s)")).toBeInTheDocument();
        expect(getByText("Select processing type(s)")).toBeInTheDocument();
    });

    test("shows a post-submit error and hides it on close", async () => {
        const errorTitle = "Data submission failed.";
        const nonFieldErrorSubtitle = "We encountered non-field specific " +
            "errors, which may be related to multiple fields or the " +
            "entire form. Please see them below:";
        const errorSupportInstructions = "If you can't resolve the issue " +
            "by updating the field values, please contact the OS Hub " +
            "team and provide the following data:";

        const updatedState = {
            ...defaultState,
            contributeProductionLocation: {
                pendingModerationEvent: {
                    data: {},
                    fetching: false,
                    error: {
                        errorSource: "CLIENT",
                        detail: "The request body is invalid.",
                        errors: [
                            {
                                field: "non_field_errors",
                                detail: "Invalid data. Expected a dictionary (object), but got list."
                            }
                        ],
                        rawData: {
                            detail: "The request body is invalid.",
                            errors: [
                                {
                                    field: "non_field_errors",
                                    detail: "Invalid data. Expected a dictionary (object), but got list."
                                }
                            ]
                        }
                    }
                },
                singleProductionLocation: {
                    data: {},
                    fetching: false,
                    error: null,
                },
            },
        };

        const { getByText, getByLabelText, queryByText } = renderComponent({}, updatedState);

        expect(getByText(errorTitle)).toBeInTheDocument();
        expect(getByText(nonFieldErrorSubtitle)).toBeInTheDocument();
        expect(getByText(errorSupportInstructions)).toBeInTheDocument();
        expect(getByText(
            "Invalid data. Expected a dictionary (object), but got list."
        )).toBeInTheDocument();

        const closeButton = getByLabelText(/close/i)
        fireEvent.click(closeButton)

        expect(queryByText(errorTitle)).not.toBeInTheDocument();
        expect(queryByText(nonFieldErrorSubtitle)).not.toBeInTheDocument();
        expect(queryByText(errorSupportInstructions)).not.toBeInTheDocument();
        expect(queryByText(
            "Invalid data. Expected a dictionary (object), but got list."
        )).not.toBeInTheDocument();
    });
});

describe("ProductionLocationInfo component, test invalid incoming data for UPDATE v1/production-locations", () => {
    const osID = 'GR2019098DC1P4A';
    const defaultState = {
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
        contributeProductionLocation: {
            singleProductionLocation: {
                data: {
                    processing_type: ['Apparel'],
                    name: 'Modelina',
                    coordinates: {
                        lat: 40.6875863,
                        lng: 22.9389083
                    },
                    os_id: osID,
                    location_type: ['Apparel'],
                    country: {
                        name: 'Greece',
                        numeric: '300',
                        alpha_3: 'GRC',
                        alpha_2: 'GR'
                    },
                    address: '1 Agiou Petrou Street, Oreokastrou, Thessaloniki, 56430',
                    claim_status: 'unclaimed',
                    sector: ['Apparel'],
                    number_of_workers: {
                        max: 150,
                        min: 0
                    },
                    product_type: ['Accessories']
                },
                fetching: false,
                error: null
            },
            productionLocations: {
                data: [],
                fetching: false,
                error: null
            },
            pendingModerationEvent: {
                data: {},
                fetching: false,
                error: null
            }
        },
    };

    const defaultProps = {
        submitMethod: "UPDATE",
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <MemoryRouter initialEntries={[`/contribute/single-location/${osID}/info/`]}>
                <Route
                    path="/contribute/single-location/:osID/info/"
                    component={() => <ProductionLocationInfo {...defaultProps} {...props} />}
                />
            </MemoryRouter>,
            { preloadedState: defaultState },
        )

    test("update button should be enabled when number of workers invalid but additional info is hidden", async () => {
        const { getByRole, getByText, getByTestId, getByPlaceholderText, queryByText } = renderComponent();
        const numberOfWorkersError = "Enter a single positive number " +
            "(e.g., 5) or a valid range (e.g., 3–10). In a range, the " +
            "minimum value must be less than or equal to the maximum, " +
            "and both must be at least 1.";

        await waitFor(() => expect(queryByText(numberOfWorkersError)).not.toBeInTheDocument());

        const updateButton = getByRole("button", { name: /Update/i });
        await waitFor(() => expect(updateButton).toBeEnabled());

        const switchButton = getByTestId("switch-additional-info-fields");
        fireEvent.click(switchButton);

        const numberOfWorkersInput = getByPlaceholderText("Enter the number of workers as a number or range");
        fireEvent.change(numberOfWorkersInput, { target: { value: '0-150' } });

        await waitFor(() => expect(numberOfWorkersInput).toHaveAttribute("aria-invalid", "true"));
        expect(getByText(numberOfWorkersError)).toBeInTheDocument();

        await waitFor(() => expect(updateButton).toBeDisabled());

        fireEvent.click(switchButton);
        await waitFor(() => expect(queryByText("Enter the number of workers as a number or range")).not.toBeInTheDocument());
        expect(updateButton).toBeEnabled();
    });
});

describe("ProductionLocationInfo component, possible duplicate submission dialog", () => {
    const defaultState = {
        filterOptions: {
            countries: {
                data: [{ value: "US", label: "United States" }],
                error: null,
                fetching: false,
            },
            facilityProcessingType: {
                data: [],
                error: null,
                fetching: false,
            },
        },
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
        featureFlags: {
            flags: {
                disable_list_uploading: false,
            },
            fetching: false,
        },
        contributeProductionLocation: {
            pendingModerationEvent: {
                data: {},
                fetching: false,
                error: {
                    errorSource: "CLIENT",
                    detail: "You recently submitted a very similar production location.",
                    errors: null,
                    rawData: {
                        detail: "You recently submitted a very similar production location.",
                        duplicate_of: {
                            moderation_id: "abc-123",
                            created_at: "2026-07-24T12:00:00.000Z",
                            name: "Blue Horizon Facility",
                            address: "990 Spring Garden St., Philadelphia PA 19123",
                            country: "US",
                            duplicate_check_window_minutes: 30,
                        },
                    },
                },
            },
            singleProductionLocation: {
                data: {},
                fetching: false,
                error: null,
            },
        },
    };

    const defaultProps = {
        submitMethod: "POST",
    };

    const renderComponent = (props = {}, preloadedState = defaultState) =>
        renderWithProviders(
            <Router>
                <ProductionLocationInfo {...defaultProps} {...props} />
            </Router>,
            { preloadedState },
        );

    const stateWithDuplicateOf = duplicateOfOverrides => {
        const baseError =
            defaultState.contributeProductionLocation.pendingModerationEvent
                .error;
        const duplicateOf = { ...baseError.rawData.duplicate_of };
        Object.keys(duplicateOfOverrides).forEach(key => {
            if (duplicateOfOverrides[key] === undefined) {
                delete duplicateOf[key];
            } else {
                duplicateOf[key] = duplicateOfOverrides[key];
            }
        });

        return {
            ...defaultState,
            contributeProductionLocation: {
                ...defaultState.contributeProductionLocation,
                pendingModerationEvent: {
                    ...defaultState.contributeProductionLocation
                        .pendingModerationEvent,
                    error: {
                        ...baseError,
                        rawData: {
                            ...baseError.rawData,
                            duplicate_of: duplicateOf,
                        },
                    },
                },
            },
        };
    };

    test("shows the duplicate submission dialog instead of the generic error notification", () => {
        const { getByText, queryByText } = renderComponent();

        expect(getByText("Possible Duplicate Submission")).toBeInTheDocument();
        expect(queryByText("Data submission failed.")).not.toBeInTheDocument();
    });

    test("dismisses the dialog on 'Go back and edit' without resubmitting", async () => {
        const { getByText, queryByText } = renderComponent();

        fireEvent.click(getByText("Go back and edit"));

        await waitFor(() =>
            expect(queryByText("Possible Duplicate Submission")).not.toBeInTheDocument(),
        );
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test("resubmits with duplicate_override when 'Submit anyway' is clicked", async () => {
        const { getByText } = renderComponent();

        fireEvent.click(getByText("Submit anyway"));

        await waitFor(() => expect(apiRequest.post).toHaveBeenCalledTimes(1));
        const [, body, config] = apiRequest.post.mock.calls[0];
        expect(body.duplicate_override).toBeUndefined();
        expect(config.params.duplicate_override).toBe(true);
    });

    test("renders the backend's duplicate check window in the dialog message", () => {
        const { getByText } = renderComponent(
            {},
            stateWithDuplicateOf({ duplicate_check_window_minutes: 45 }),
        );

        expect(getByText(/wait at least 45 minutes/)).toBeInTheDocument();
    });

    test("falls back to the default window when the backend omits it", () => {
        const { getByText } = renderComponent(
            {},
            stateWithDuplicateOf({
                duplicate_check_window_minutes: undefined,
            }),
        );

        expect(getByText(/wait at least 30 minutes/)).toBeInTheDocument();
    });
});

describe("ProductionLocationInfo component, server-side submission quality warnings dialog", () => {
    const defaultState = {
        filterOptions: {
            countries: {
                data: [{ value: "US", label: "United States" }],
                error: null,
                fetching: false,
            },
            facilityProcessingType: {
                data: [],
                error: null,
                fetching: false,
            },
        },
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
        featureFlags: {
            flags: {
                disable_list_uploading: false,
            },
            fetching: false,
        },
        contributeProductionLocation: {
            pendingModerationEvent: {
                data: {},
                fetching: false,
                error: {
                    errorSource: "CLIENT",
                    detail: "This submission may have one or more data-quality issues. Please review the warnings below.",
                    errors: null,
                    rawData: {
                        detail: "This submission may have one or more data-quality issues. Please review the warnings below.",
                        warnings: [
                            {
                                type: "name_quality",
                                title: "Name May Not Look Like a Facility Name",
                                message: "The name looks like test data.",
                            },
                            {
                                type: "address_country_mismatch",
                                title: "Address May Not Match Selected Country",
                                message: "The address does not appear to be in the selected country.",
                            },
                        ],
                    },
                },
            },
            singleProductionLocation: {
                data: {},
                fetching: false,
                error: null,
            },
        },
    };

    const defaultProps = {
        submitMethod: "POST",
    };

    const renderComponent = (props = {}, preloadedState = defaultState) =>
        renderWithProviders(
            <Router>
                <ProductionLocationInfo {...defaultProps} {...props} />
            </Router>,
            { preloadedState },
        );

    test("shows every returned server-side warning together in one dialog", () => {
        const { getByText, queryByText } = renderComponent();

        expect(getByText("Please Review Before Submitting")).toBeInTheDocument();
        expect(getByText("Name May Not Look Like a Facility Name")).toBeInTheDocument();
        expect(getByText("Address May Not Match Selected Country")).toBeInTheDocument();
        expect(queryByText("Data submission failed.")).not.toBeInTheDocument();
    });

    test("dismisses the dialog on 'Go back and edit' without resubmitting", async () => {
        const { getByText, queryByText } = renderComponent();

        fireEvent.click(getByText("Go back and edit"));

        await waitFor(() =>
            expect(queryByText("Please Review Before Submitting")).not.toBeInTheDocument(),
        );
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test("resubmits with ignore_warnings when 'Submit anyway' is clicked", async () => {
        const { getByText } = renderComponent();

        fireEvent.click(getByText("Submit anyway"));

        await waitFor(() => expect(apiRequest.post).toHaveBeenCalledTimes(1));
        const [, body, config] = apiRequest.post.mock.calls[0];
        expect(body.ignore_warnings).toBeUndefined();
        expect(config.params.ignore_warnings).toBe(true);
    });
});

describe("ProductionLocationInfo component, override accumulation across the duplicate and quality warning dialogs", () => {
    const duplicateRawData = {
        detail: "You recently submitted a very similar production location.",
        duplicate_of: {
            moderation_id: "abc-123",
            created_at: "2026-07-24T12:00:00.000Z",
            name: "Blue Horizon Facility",
            address: "990 Spring Garden St., Philadelphia PA 19123",
            country: "US",
            duplicate_check_window_minutes: 30,
        },
    };

    const warningsRawData = {
        detail: "This submission may have one or more data-quality issues. Please review the warnings below.",
        warnings: [
            {
                type: "name_quality",
                title: "Name May Not Look Like a Facility Name",
                message: "The name looks like test data.",
            },
        ],
    };

    const stateWithError = rawData => ({
        filterOptions: {
            countries: {
                data: [{ value: "US", label: "United States" }],
                error: null,
                fetching: false,
            },
            facilityProcessingType: {
                data: [],
                error: null,
                fetching: false,
            },
        },
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
        featureFlags: {
            flags: {
                disable_list_uploading: false,
            },
            fetching: false,
        },
        contributeProductionLocation: {
            pendingModerationEvent: {
                data: {},
                fetching: false,
                error: {
                    errorSource: "CLIENT",
                    detail: rawData.detail,
                    errors: null,
                    rawData,
                },
            },
            singleProductionLocation: {
                data: {},
                fetching: false,
                error: null,
            },
        },
    });

    const renderComponent = preloadedState =>
        renderWithProviders(
            <Router>
                <ProductionLocationInfo submitMethod="POST" />
            </Router>,
            { preloadedState },
        );

    test("carries the granted duplicate override when confirming the quality warnings dialog", async () => {
        apiRequest.post.mockRejectedValue({
            response: { status: 422, data: warningsRawData },
        });

        const { getByText, getAllByText } = renderComponent(
            stateWithError(duplicateRawData),
        );

        fireEvent.click(getByText("Submit anyway"));

        await waitFor(() => expect(apiRequest.post).toHaveBeenCalledTimes(1));
        expect(apiRequest.post.mock.calls[0][2].params).toEqual({
            duplicate_override: true,
        });

        // Wait for the quality warnings dialog to open AND the duplicate
        // dialog to finish its exit transition, so there is only one
        // 'Submit anyway' button left in the document.
        await waitFor(() => {
            expect(getByText("Name May Not Look Like a Facility Name")).toBeInTheDocument();
            expect(getAllByText("Submit anyway")).toHaveLength(1);
        });

        fireEvent.click(getByText("Submit anyway"));

        await waitFor(() => expect(apiRequest.post).toHaveBeenCalledTimes(2));
        expect(apiRequest.post.mock.calls[1][2].params).toEqual({
            duplicate_override: true,
            ignore_warnings: true,
        });
    });

    test("carries the granted quality override when confirming the duplicate dialog", async () => {
        apiRequest.post.mockRejectedValue({
            response: { status: 409, data: duplicateRawData },
        });

        const { getByText, getAllByText } = renderComponent(
            stateWithError(warningsRawData),
        );

        fireEvent.click(getByText("Submit anyway"));

        await waitFor(() => expect(apiRequest.post).toHaveBeenCalledTimes(1));
        expect(apiRequest.post.mock.calls[0][2].params).toEqual({
            ignore_warnings: true,
        });

        // Wait for the duplicate dialog to open AND the quality warnings
        // dialog to finish its exit transition, so there is only one
        // 'Submit anyway' button left in the document.
        await waitFor(() => {
            expect(getByText("Possible Duplicate Submission")).toBeInTheDocument();
            expect(getAllByText("Submit anyway")).toHaveLength(1);
        });

        fireEvent.click(getByText("Submit anyway"));

        await waitFor(() => expect(apiRequest.post).toHaveBeenCalledTimes(2));
        expect(apiRequest.post.mock.calls[1][2].params).toEqual({
            duplicate_override: true,
            ignore_warnings: true,
        });
    });
});
