def float_comparison(digits=0):
    """
    Generate function for comparison float numbers with given precision
    @param digits: the numbers of significant digits after coma
    @return: Boolean
    """

    def comparison(right_answer, user_answer):
        if not isinstance(user_answer, (int, float)):
            return False, "It's not a number"
        precision = 0.1 ** digits
        return right_answer - precision <= user_answer <= right_answer + precision, None

    return comparison