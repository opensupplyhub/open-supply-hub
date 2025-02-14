import React from "react";
import { fireEvent } from "@testing-library/react";
import SearchByNameAndAddressTab from "../../components/Contribute/SearchByNameAndAddressTab";
import { searchByNameAndAddressResultRoute } from "../../util/constants";
import renderWithProviders from "../../util/testUtils/renderWithProviders";


const mockPush = jest.fn();

jest.mock("react-router-dom", () => {
    const actual = jest.requireActual("react-router-dom");
    return {
        ...actual,
        useHistory: () => ({
            push: mockPush,
        }),
    };
});

jest.mock("../../components/Filters/StyledSelect", () => (props) => {
    const { options, value, onChange, onBlur, placeholder } = props;
    return (
        <select
            data-testid="countries-select"
            value={value ? value.value : ""}
            onChange={(e) => {
                const selectedOption = options.find(
                    (opt) => opt.value === e.target.value,
                );
                onChange(selectedOption);
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

describe("SearchByNameAndAddressTab component", () => {
    const countriesData = [
        { value: "GB", label: "United Kingdom" },
        { value: "US", label: "United States" },
    ];

    const defaultState = {
        filterOptions: {
            countries: {
                data: countriesData,
                error: null,
                fetching: false,
            },
        },
    };

    test("renders loading indicator when fetching is true", () => {
        const { getByRole } = renderWithProviders(
            <SearchByNameAndAddressTab />,
            {
                preloadedState: {
                    filterOptions: {
                        countries: {
                            data: countriesData,
                            error: null,
                            fetching: true,
                        },
                    },
                },
            },
        );

        expect(getByRole("progressbar")).toBeInTheDocument();
    });

    test("renders error message when error is provided", () => {
        const errorMsg = "An error occurred";
        const { getByText } = renderWithProviders(
            <SearchByNameAndAddressTab />,
            {
                preloadedState: {
                    filterOptions: {
                        countries: {
                            data: countriesData,
                            error: [errorMsg],
                            fetching: false,
                        },
                    },
                },
            },
        );
        expect(getByText(errorMsg)).toBeInTheDocument();
    });

    test("renders form fields and disabled Search button by default", () => {
        const { getByText, getByRole, getByPlaceholderText, getByTestId } =
            renderWithProviders(<SearchByNameAndAddressTab />, {
                preloadedState: defaultState,
            });

        expect(
            getByText(/Check if the production location is already on OS Hub/i),
        ).toBeInTheDocument();
        expect(getByText("Production Location Details")).toBeInTheDocument();
        expect(getByText("Enter the Name")).toBeInTheDocument();
        expect(getByText("Enter the Address")).toBeInTheDocument();
        expect(getByText("Select the Country")).toBeInTheDocument();

        const nameInput = getByPlaceholderText("Type a name");
        expect(nameInput).toBeInTheDocument();
        expect(nameInput).toHaveValue("");

        const addressInput = getByPlaceholderText("Address");
        expect(addressInput).toBeInTheDocument();
        expect(addressInput).toHaveValue("");

        const countrySelect = getByTestId("countries-select");
        expect(countrySelect).toBeInTheDocument();
        expect(countrySelect).toHaveValue("");

        const searchButton = getByRole("button", { name: /Search/i });
        expect(searchButton).toBeDisabled();
    });

    test("enables the Search button when all fields are filled", () => {
        const { getByRole, getByPlaceholderText, getByTestId } =
            renderWithProviders(<SearchByNameAndAddressTab />, {
                preloadedState: defaultState,
            });

        const nameInput = getByPlaceholderText("Type a name");
        const addressInput = getByPlaceholderText("Address");
        const countrySelect = getByTestId("countries-select");
        const searchButton = getByRole("button", { name: /Search/i });

        expect(searchButton).toBeDisabled();

        fireEvent.change(nameInput, { target: { value: "Test Name" } });
        fireEvent.change(addressInput, { target: { value: "Test Address" } });
        fireEvent.change(countrySelect, { target: { value: "US" } });

        expect(countrySelect.value).toBe("US");
        expect(searchButton).toBeEnabled();

        const searchParams = new URLSearchParams({
            name: "Test Name",
            address: "Test Address",
            country: "US",
        });
        const expectedUrl = `${searchByNameAndAddressResultRoute}?${searchParams.toString()}`;

        fireEvent.click(searchButton);
        expect(mockPush).toHaveBeenCalledWith(expectedUrl);
    });

    test("shows error indication on blur when fields are empty", () => {
        const { getByText, getAllByText, getByTestId, getByPlaceholderText } =
            renderWithProviders(<SearchByNameAndAddressTab />, {
                preloadedState: defaultState,
            });
        const nameInput = getByPlaceholderText("Type a name");
        const addressInput = getByPlaceholderText("Address");
        const countrySelect = getByTestId("countries-select");

        fireEvent.blur(nameInput);
        fireEvent.blur(addressInput);
        fireEvent.blur(countrySelect);

        expect(getByPlaceholderText("Type a name")).toHaveAttribute(
            "aria-invalid",
            "true",
        );
        expect(getByPlaceholderText("Address")).toHaveAttribute(
            "aria-invalid",
            "true",
        );
        expect(getAllByText(/This field is required./i)).toHaveLength(2);
        expect(
            getByText(
                /The country is missing from your search. Select the correct country from the drop down menu./i,
            ),
        ).toBeInTheDocument();
    });
});
