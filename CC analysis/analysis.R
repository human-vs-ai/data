library(ggplot2)
data= read.csv("results_stage_2_analysis.csv")

# Convert factor columns to numeric
complete_data$responses.ai.0 <- as.numeric(as.character(complete_data$responses.ai.0))
complete_data$responses.human.0 <- as.numeric(as.character(complete_data$responses.human.0))

# Conduct a paired t-test on the numeric data
result <- t.test(complete_data$responses.ai.0, complete_data$responses.human.0, paired = TRUE)

# Print the result
result


combined_data_1 <- rbind(data.frame(rating = data$responses.human.0, source = "Human"),
                       data.frame(rating = data$responses.ai.0, source = "AI"))

# Plot the combined histogram
ggplot(combined_data_1, aes(x = rating, fill = source)) +
  geom_histogram(position = "dodge", bins = 20, alpha = 0.5, color = "black") +
  labs(x = "Rating", y = "Frequency", title = "Distribution of Human and AI Ratings") +
  scale_fill_manual(values = c("steelblue", "darkorange")) +
  theme_minimal()


combined_data_2 <- data.frame(
  Source = rep(c("Human", "AI"), each = nrow(data)),
  Rating = c(data$responses.human.0, data$responses.ai.0)
)

# Plot the combined box plot
ggplot(combined_data_2, aes(x = Source, y = Rating, fill = Source)) +
  geom_boxplot() +
  labs(x = "Source", y = "Rating", title = "Comparison of Human and AI Ratings") +
  scale_fill_manual(values = c("steelblue", "darkorange")) +
  theme_minimal()


ggplot(data, aes(x = "", y = responses.verdict)) +
  geom_boxplot() +
  labs(x = "", y = "Verdict", title = "Box Plot of Verdict") +
  theme_minimal()


ggplot(data, aes(x = responses.verdict)) +
  geom_histogram(binwidth = 1, fill = "steelblue", color = "black") +
  labs(x = "Verdict", y = "Frequency", title = "Distribution of Verdict") +
  theme_minimal()


# Create a named vector to map original values to desired names
value_names <- c("AI", "Human", "No preference")

# Calculate the frequencies of each value in the column
value_counts <- table(data$responses.verdict)

# Calculate the percentages
percentages <- prop.table(value_counts) * 100

# Change the names of the percentages using the named vector
names(percentages) <- value_names

# Print the percentages
print(percentages)
