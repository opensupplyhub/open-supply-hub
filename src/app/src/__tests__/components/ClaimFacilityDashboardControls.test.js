import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import DashboardClaimsDetailsControls from "../../components/DashboardClaimDetailsControls";
import apiRequest from "../../util/apiRequest";

jest.mock("../../util/apiRequest", () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
  },
}));

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

const renderComponent = (store, props) =>
  render(
    <Provider store={store}>
      <DashboardClaimsDetailsControls {...props} />
    </Provider>,
  );

describe("DashboardClaimsDetailsControls", () => {
  const defaultProps = {
    data: {
      id: 1,
      status: "PENDING",
      created_at: "2020-01-01T00:00:00Z",
      updated_at: "2020-01-01T00:00:00Z",
      contact_person: "John Doe",
      job_title: "Manager",
      email: "john@gmail.com",
      phone_number: "123-456-7890",
      company_name: "Test Company",
      website: "http://www.test.com",
      facility_description: "Test description",
      linkedin_profile: "http://www.linkedin.com",
      contributor: {},
      facility: {
        id: "1",
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [-122.4194, 37.7749],
        },
        properties: {
          name: "Test Facility",
          address: "123 Test St",
          country_code: "US",
          country_name: "United States",
        },
      },
      status_change: {
        status_change_by: "",
        status_change_date: "",
        status_change_reason: "",
      },
      notes: [],
      attachments: [],
    },
    fetching: false,
    error: null,
    messageClaimant: jest.fn(),
    approveClaim: jest.fn(),
    denyClaim: jest.fn(),
    revokeClaim: jest.fn(),
  };

  let store;

  beforeEach(() => {
    store = mockStore({
      claimFacilityDashboard: {
        statusControls: {
          fetching: false,
          error: null,
        },
      },
    });

    apiRequest.post.mockClear();
  });

  test("renders without crashing", () => {
    renderComponent(store, defaultProps);
  });

  test("renders correct buttons for pending status", () => {
    const { getByText, queryByText } = renderComponent(store, defaultProps);
    expect(getByText("Message Claimant")).toBeInTheDocument();
    expect(getByText("Approve Claim")).toBeInTheDocument();
    expect(getByText("Deny Claim")).toBeInTheDocument();
    expect(queryByText("Revoke Claim")).not.toBeInTheDocument();
  });

  test("renders correct button for approved status", () => {
    const props = {
      ...defaultProps,
      data: { ...defaultProps.data, status: "APPROVED" },
    };
    const { getByText, queryByText } = renderComponent(store, props);
    expect(getByText("Revoke Claim")).toBeInTheDocument();
    expect(queryByText("Message Claimant")).not.toBeInTheDocument();
    expect(queryByText("Approve Claim")).not.toBeInTheDocument();
    expect(queryByText("Deny Claim")).not.toBeInTheDocument();
  });

  test("toggles message dialog visibility", async () => {
    const { getByText, getByLabelText, queryByText } = renderComponent(
      store,
      defaultProps,
    );
    fireEvent.click(getByText("Message Claimant"));
    expect(getByText("Send a message to claimant?")).toBeInTheDocument();
    expect(
      getByLabelText(
        "Enter a message. (This will be emailed to the contact email associated with this claim.)",
      ),
    ).toBeInTheDocument();
    fireEvent.click(getByText("Cancel"));
    await waitFor(() => {
      expect(
        queryByText("Send a message to claimant?"),
      ).not.toBeInTheDocument();
    });
  });

  test("updates message to claimant text", async () => {
    const { getByText, getByLabelText } = renderComponent(store, defaultProps);
    fireEvent.click(getByText("Message Claimant"));
    const input = getByLabelText(
      "Enter a message. (This will be emailed to the contact email associated with this claim.)",
    );
    fireEvent.change(input, { target: { value: "Message to claimant." } });
    expect(input.value).toBe("Message to claimant.");
  });

  test("handles message claimant action with successful response", async () => {
    const message = "Message to claimant.";
    const expectedSuccessAction = {
      error: false,
      payload: {
        notes: [{ id: 1, note: "Message to claimant." }],
      },
      type: "COMPLETE_MESSAGE_FACILITY_CLAIMANT",
    };
    apiRequest.post.mockResolvedValue({
      data: { notes: [{ id: 1, note: message }] },
    });

    const { getByText, getByLabelText } = renderComponent(store, defaultProps);
    fireEvent.click(getByText("Message Claimant"));
    const input = getByLabelText(
      "Enter a message. (This will be emailed to the contact email associated with this claim.)",
    );
    fireEvent.change(input, { target: { value: message } });
    fireEvent.click(getByText("message"));

    await waitFor(() => {
      expect(apiRequest.post).toHaveBeenCalledWith(expect.anything(), {
        message,
      });
      expect(store.getActions()).toContainEqual(expectedSuccessAction);
    });
  });

  test("handles message claimant action with failed response", async () => {
    const message = "Message to claimant.";
    const expectedFailureAction = {
      error: false,
      payload: ["An error prevented messaging to facility claimant"],
      type: "FAIL_MESSAGE_FACILITY_CLAIMANT",
    };
    apiRequest.post.mockRejectedValue(new Error("Failed to message claimant."));

    const { getByText, getByLabelText } = renderComponent(store, defaultProps);
    fireEvent.click(getByText("Message Claimant"));
    const input = getByLabelText(
      "Enter a message. (This will be emailed to the contact email associated with this claim.)",
    );
    fireEvent.change(input, { target: { value: message } });
    fireEvent.click(getByText("message"));

    await waitFor(() => {
      expect(apiRequest.post).toHaveBeenCalledWith(expect.anything(), {
        message,
      });
      expect(store.getActions()).toContainEqual(expectedFailureAction);
    });
  });
});
