import mongoengine as db


class Rankings(db.Document):
    year = db.IntField()
    overall = db.DynamicField()  # Field to store overall rankings
    top_10 = db.DynamicField()  # Field to store top 10 scorecards
    cwa = db.DynamicField()
    attempted = db.DynamicField()

#     @classmethod
#     def convert_scorecard_df_to_json(cls, df):
#         """
#         Converts a DataFrame of scorecards to a nested JSON structure.
#
#         Args:
#             df (pandas.DataFrame): DataFrame containing scorecard data.
#
#         Returns:
#             dict: Nested JSON object representing the scorecard data.
#         """
#         # Assuming your DataFrame is named 'df'
#         json_data = df.to_json(orient='index', force_ascii=False)
#
#         # Convert the JSON string to a dictionary
#         json_obj = json.loads(json_data)
#
#         # Create a new dictionary with modified structure
#         modified_json_obj = {}
#         for key, value in json_obj.items():
#             rider_id, section = eval(key)
#             if rider_id not in modified_json_obj:
#                 modified_json_obj[rider_id] = {}
#             if section not in modified_json_obj[rider_id]:
#                 modified_json_obj[rider_id][section] = {}
#             for stat_name, stat_value in value.items():
#                 stat_category, stat_percentile = stat_name.strip("(')").split("', ")
#                 if stat_category not in modified_json_obj[rider_id][section]:
#                     modified_json_obj[rider_id][section][stat_category] = {}
#                 modified_json_obj[rider_id][section][stat_category][stat_percentile.strip("'")] = stat_value
#
#         return modified_json_obj
#
#     @classmethod
#     def rankings_df(cls, contest_id=None, landed=True, start_date=None, end_date=None, rider_id=None):
#         """
#         Generates a DataFrame summarizing the scorecard data for rankings.
#
#         Args:
#             contest_id (str): ID of the contest.
#             landed (bool): Whether the tricks were landed or not.
#             start_date (datetime): Start date for filtering scorecards.
#             end_date (datetime): End date for filtering scorecards.
#             rider_id (str): ID of the rider.
#
#         Returns:
#             pandas.DataFrame: DataFrame containing the scorecard summary.
#         """
#         df = Scorecard.to_dataframe(landed=landed, start_date=start_date, end_date=end_date, contest_id=contest_id,
#                                     rider_id=rider_id)
#         df_sorted = df.sort_values(['rider.$oid', 'score'], ascending=[True, False])
#         grouped = df_sorted.groupby(['rider.$oid', 'section'])
#         df.reset_index(inplace=True)
#         scorecard_summary = grouped.describe()
#         return scorecard_summary
#
#     def update_overall(self):
#         """
#         Updates the 'overall' field with the overall rankings based on the scorecard data.
#         """
#         current_year = datetime.now().year
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31)
#         self.overall = self.convert_scorecard_df_to_json(self.rankings_df(start_date=start_date, end_date=end_date))
#
#     def update_top_ten(self):
#         """
#         Updates the 'top_10' field with the top 10 scorecards for each rider.
#         """
#         current_year = datetime.now().year
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31)
#
#         # Get the rankings DataFrame
#         df = self.rankings_df(start_date=start_date, end_date=end_date)
#
#         # Filter the DataFrame to get the top 10 scorecards for each rider
#         top_10_df = df.groupby(['rider.$oid']).apply(lambda x: x.nlargest(10, 'score'))
#
#         # Convert the top 10 DataFrame to JSON format
#         top_10_json = self.convert_scorecard_df_to_json(top_10_df)
#
#         # Update the top_10 field with the JSON data
#         self.top_10 = top_10_json
