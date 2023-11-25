from datetime import datetime, timedelta


class PeriodPredictor:
    def __init__(self):
        self.user_data = {}

    def add_period_dates(self, username):
        if username not in self.user_data:
            self.user_data[username] = []

        while True:
            date_input = input("Enter a period date (YYYY-MM-DD) or 'done' to finish: ")
            if date_input.lower() == 'done':
                break

            try:
                date = datetime.strptime(date_input, '%Y-%m-%d')
                self.user_data[username].append(date)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

    def predict_next_period(self, username):
        if username in self.user_data and len(self.user_data[username]) >= 2:
            period_dates = sorted(self.user_data[username])
            cycle_lengths = [period_dates[i] - period_dates[i - 1] for i in range(1, len(period_dates))]
            average_cycle_length = sum(cycle_lengths, timedelta()) // len(cycle_lengths)
            last_period_date = period_dates[-1]
            predicted_next_period = last_period_date + average_cycle_length

            print(f"Predicted next period date for {username}: {predicted_next_period.date()}")
        else:
            print(f"Not enough data for {username} to predict. Please enter at least two past period dates.")


if __name__ == "__main__":
    predictor = PeriodPredictor()

    while True:
        choice = input("Enter 'add' to add period dates, 'predict' to predict next period, or 'exit' to quit: ")

        if choice == 'add':
            username = input("Enter username: ")
            predictor.add_period_dates(username)
        elif choice == 'predict':
            username = input("Enter username to predict next period: ")
            predictor.predict_next_period(username)
        elif choice == 'exit':
            break
        else:
            print("Invalid choice. Please enter 'add', 'predict', or 'exit'.")
