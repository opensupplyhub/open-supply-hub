import { renderHook, act } from '@testing-library/react-hooks';
import { useCheckboxManager } from '../../util/hooks';
import { CONFIRM_ACTION, REJECT_ACTION, MERGE_ACTION } from '../../util/constants';


describe('useCheckboxManager', () => {  
    test('Should initialize with default state', () => {
      const { result } = renderHook(() => useCheckboxManager());
  
      expect(result.current.action).toBe(CONFIRM_ACTION);
      expect(result.current.activeCheckboxes).toEqual([]);
      expect(result.current.activeSubmitButton).toBe(false);
    });
  
    test('handleSelectChange should update action and reset checkboxes', () => {
      const { result } = renderHook(() => useCheckboxManager());
  
      act(() => {
        result.current.handleSelectChange(REJECT_ACTION);
      });
  
      expect(result.current.action).toBe(REJECT_ACTION);
      expect(result.current.activeCheckboxes).toEqual([]);
      expect(result.current.activeSubmitButton).toBe(false);
    });
  
    test('toggleCheckbox should handle confirm selection correctly', () => {
      const { result } = renderHook(() => useCheckboxManager());
  
      const facility = { id: 1, name: 'Facility test name' };
  
      act(() => {
        result.current.toggleCheckbox(facility);
      });
  
      expect(result.current.activeCheckboxes).toEqual([facility]);
    });
  
    test('toggleCheckbox should handle reject selection correctly', () => {
      const { result } = renderHook(() => useCheckboxManager());
  
      act(() => {
        result.current.handleSelectChange(REJECT_ACTION);
      });
  
      const facility = { id: 1, name: 'Facility test name' };
  
      act(() => {
        result.current.toggleCheckbox(facility);
      });
  
      expect(result.current.activeCheckboxes).toContain(facility);
  
      // Toggle the same facility again to remove it
      act(() => {
        result.current.toggleCheckbox(facility);
      });
  
      expect(result.current.activeCheckboxes).not.toContain(facility);
    });

    test('toggleCheckbox should handle merge selection correctly', () => {
        const { result } = renderHook(() => useCheckboxManager());
    
        act(() => {
            result.current.handleSelectChange(MERGE_ACTION);
        });
    
        const facility1 = { id: 1, name: 'Facility 1' };
        const facility2 = { id: 2, name: 'Facility 2' };
        const facility3 = { id: 3, name: 'Facility 3' };
    
        act(() => {
            result.current.toggleCheckbox(facility1);
        });
    
        expect(result.current.activeCheckboxes).toContainEqual(facility1);
        expect(result.current.activeCheckboxes.length).toBe(1);
    
        act(() => {
            result.current.toggleCheckbox(facility2);
        });
    
        // Both facilities should now be in activeCheckboxes
        expect(result.current.activeCheckboxes).toContainEqual(facility1);
        expect(result.current.activeCheckboxes).toContainEqual(facility2);
        expect(result.current.activeCheckboxes.length).toBe(2);
    
        // Attempt to select a third facility, which should be ignored
        act(() => {
            result.current.toggleCheckbox(facility3);
        });
    
        // The activeCheckboxes should still only contain the first two facilities to merge
        expect(result.current.activeCheckboxes).not.toContainEqual(facility3);
        expect(result.current.activeCheckboxes.length).toBe(2);
    
        // Now, deselect one of the facilities
        act(() => {
            result.current.toggleCheckbox(facility1);
        });
    
        expect(result.current.activeCheckboxes).not.toContainEqual(facility1);
        expect(result.current.activeCheckboxes).toContainEqual(facility2);
        expect(result.current.activeCheckboxes.length).toBe(1);
    });
    
  });
  