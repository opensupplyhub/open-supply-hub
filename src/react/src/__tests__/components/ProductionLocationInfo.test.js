import React from "react";
import { fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, BrowserRouter as Router } from "react-router-dom";

import ProductionLocationInfo from "../../components/Contribute/ProductionLocationInfo";
import renderWithProviders from "../../util/testUtils/renderWithProviders";
import { MAINTENANCE_MESSAGE } from "../../util/constants";

beforeAll(() => {
    window.scrollTo = jest.fn();
});

jest.mock('@material-ui/core/Popper', () => ({ children }) => children);
jest.mock('@material-ui/core/Portal', () => ({ children }) => children);

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
                                detail: "Invalid data. Expected a dictionary (object), but got dict."
                            }
                        ],
                        rawData: {
                            detail: "The request body is invalid.",
                            errors: [
                                {
                                    field: "non_field_errors",
                                    detail: "Invalid data. Expected a dictionary (object), but got dict."
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
            "Invalid data. Expected a dictionary (object), but got dict."
        )).toBeInTheDocument();

        const closeButton = getByLabelText(/close/i)
        fireEvent.click(closeButton)

        expect(queryByText(errorTitle)).not.toBeInTheDocument();
        expect(queryByText(nonFieldErrorSubtitle)).not.toBeInTheDocument();
        expect(queryByText(errorSupportInstructions)).not.toBeInTheDocument();
        expect(queryByText(
            "Invalid data. Expected a dictionary (object), but got dict."
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
