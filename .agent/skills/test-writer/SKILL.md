---
name: test-writer
description: >-
  Write tests for the Open Supply Hub codebase — both React (Jest + Testing
  Library) and Django (TestCase / APITestCase). Use when the user asks to add,
  write, or generate tests for a component, utility, serializer, view, or
  any other piece of the codebase.
---

# Test Writer

## Step 1 — Locate the code under test

Read the file(s) being tested to understand inputs, outputs, and edge cases before writing a single line of test code.

## Step 2 — Find a recent reference test

Before writing, find the most recent test file for the same layer and domain:

```bash
# Most recently modified React tests
ls -t src/react/src/__tests__/**/*.test.js | head -5

# Most recently modified Django tests
ls -t src/django/api/tests/test_*.py | head -5
```

Read at least one of those files and match its style exactly.

---

## React tests

**Location**: `src/react/src/__tests__/` — mirror the `src/` directory tree.

### Utility / schema tests (no DOM)

```js
import { myUtil } from '../../util/myUtil';

describe('myUtil', () => {
    it('returns expected value for valid input', () => {
        expect(myUtil('input')).toBe('expected');
    });

    it('throws for invalid input', () => {
        expect(() => myUtil(null)).toThrow('error message');
    });
});
```

For async (e.g. Yup schemas):
```js
await expect(schema.isValid(validData)).resolves.toBe(true);
await expect(schema.validate(badData)).rejects.toThrow('message');
```

### Component tests (DOM)

```js
import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '../../util/testUtils/renderWithProviders';
import MyComponent from '../../components/MyComponent/MyComponent';

const defaultProps = { label: 'Test', onClick: jest.fn() };

describe('MyComponent', () => {
    it('renders the label', () => {
        renderWithProviders(<MyComponent {...defaultProps} />);
        expect(screen.getByText('Test')).toBeInTheDocument();
    });

    it('calls onClick when clicked', () => {
        renderWithProviders(<MyComponent {...defaultProps} />);
        fireEvent.click(screen.getByRole('button'));
        expect(defaultProps.onClick).toHaveBeenCalledTimes(1);
    });
});
```

With Redux preloaded state:
```js
renderWithProviders(<MyComponent />, {
    preloadedState: { someSlice: { data: [] } },
});
```

### Rules
- Nested `describe` / `it` structure — always.
- `jest.fn()` for callbacks; reset with `jest.clearAllMocks()` in `beforeEach` when sharing mocks.
- Prefer `getByRole` / `getByText` / `getByLabelText` over `getByTestId`.
- Use `waitFor` for async state updates only when necessary.
- Never import internal MUI or third-party internals directly.

---

## Django tests

**Location**: `src/django/api/tests/test_<domain>.py`

### Serializer / unit tests

```python
from django.test import TestCase
from api.serializers.my_serializer import MySerializer

class MySerializerTest(TestCase):
    fixtures = ['relevant_fixture']

    def setUp(self):
        # DB prep — delete conflicting seed data if needed
        pass

    def test_returns_expected_fields(self):
        serializer = MySerializer()
        result = serializer.to_representation(obj)
        self.assertEqual(result['field'], 'expected_value')
```

### API / view tests

```python
from django.urls import reverse
from rest_framework import status
from api.tests.base import FacilityAPITestCaseBase  # or APITestCase

class MyViewTest(FacilityAPITestCaseBase):
    fixtures = ['relevant_fixture']

    def test_returns_200_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('my-endpoint')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)

    def test_returns_403_for_anonymous(self):
        response = self.client.get(reverse('my-endpoint'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

With waffle feature flags:
```python
from waffle.testutils import override_flag

class MyFlaggedFeatureTest(FacilityAPITestCaseBase):
    @override_flag('my_flag', active=True)
    def test_feature_enabled(self):
        ...

    @override_flag('my_flag', active=False)
    def test_feature_disabled(self):
        ...
```

With mocking:
```python
from unittest.mock import patch

@patch('api.services.my_service.external_call')
def test_handles_external_error(self, mock_call):
    mock_call.side_effect = Exception('connection refused')
    response = self.client.get(reverse('my-endpoint'))
    self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Rules
- Use `self.assertEqual` / `self.assertIn` / `self.assertTrue` — no third-party assertion libraries.
- One assertion theme per test method; keep methods short and named clearly.
- Use `fixtures` for DB state; avoid raw `Model.objects.create` chains unless the fixture approach is impractical.
- Always clean up seed data in `setUp` when migrations may pre-populate the DB.

---

## Step 3 — Run the tests

```bash
# React
docker compose exec react yarn test --watchAll=false --testPathPattern=<TestFileName>

# Django
docker compose exec django python manage.py test api.tests.test_<module>
```

Fix all failures before presenting the tests.
