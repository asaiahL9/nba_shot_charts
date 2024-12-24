class Video:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

    def calculate_expression(self, x, y, z):
        # Calling other methods within the class
        sum_result = self.add(x, y)
        product_result = self.multiply(sum_result, z)
        return product_result