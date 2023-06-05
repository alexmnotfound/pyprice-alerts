from helper.google import SheetsHelper


def main():
    # Initialize the SheetsHelper object
    helper = SheetsHelper()

    # Read data from the sheet
    sheet_id = '1N241PKX1ljVapIDu15EW_E_Y6q2O7TZmoKODv7X88Rs'
    sheet_range = 'Panel!B5:Z'
    print(f"Reading data from range {sheet_range} of the Spreadsheet {sheet_id}\n")
    data = helper.get_sheet_data(sheet_id, sheet_range)
    print(data)


if __name__ == '__main__':
    main()
