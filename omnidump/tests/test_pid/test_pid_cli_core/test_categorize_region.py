"""Test for Function categorize_region (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import categorize_regions

def test_cr_success(
        mock_process_lines,
        mock_get_region_category,
        mock_dict_data
):
    """
    Full Cycle test
    
    Goal: Verify all components interact correctly and regions are sorted. 

    Assertions: Assert the returned dictionary has two entries in ["executable"] (dict A, C) 
                and one entry in ["heap"] (dict B). 
    """
    dict_a = mock_dict_data["dict_a"]
    dict_b = mock_dict_data["dict_b"]
    dict_c = mock_dict_data["dict_c"]

    file_content = ["line1", "line2", "line3"]
    mock_process_lines.side_effect = [dict_a, dict_b, dict_c]
    mock_get_region_category.side_effect = ["executable", "heap", "executable"]
    result = categorize_regions(file_content)

    #Assert 1
    mock_process_lines.assert_any_call("line1")
    mock_process_lines.assert_any_call("line2")
    mock_process_lines.assert_any_call("line3")
    assert mock_process_lines.call_count == 3

    #Assert 2
    mock_get_region_category.assert_any_call(dict_a)
    mock_get_region_category.assert_any_call(dict_b)
    mock_get_region_category.assert_any_call(dict_c)
    assert mock_get_region_category.call_count == 3

    #Assert 3
    assert result["executable"] == [dict_a, dict_c]

    assert result["heap"] == [dict_b]

def test_cr_empty_input(
        mock_process_lines,
        mock_get_region_category
):
    """
    Empty Input

    Goal: Verify the function handles an empty list of lines gracefully

    Assertations: Assert dict_A is in the ["heap"] list and the ["stack"] list remains empty
    """
    file_content = []
    result = categorize_regions(file_content)

    mock_process_lines.assert_not_called()
    mock_get_region_category.assert_not_called()

    for category_list in result.values():
        assert category_list == []

def test_cr_skip_invalid_lines(
   mock_process_lines,
   mock_get_region_category,
   mock_dict_data,
):
    """
    Skip Invalid Lines

    Goal: Verify lines where process_lines fails (returns None or empty result) 
          are correctly skipped without error.

    Assertions: Assert dict_A is in the ["heap"] list, and the ["stack"] list remains empty. 
    """
    dict_a = mock_dict_data["dict_a"]
    mock_process_lines.side_effect = [dict_a, None]
    mock_get_region_category.return_value = "heap"
