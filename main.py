class Minterm:
    def __init__(self, dec, size):
        self.dec_value = dec
        self.bin_value = bin(dec)[2:]
        self.bin_value = "".join([(size-len(self.bin_value))*"0", self.bin_value])
        self.str_value = ""
        self.checked = False
        self.covered = False

        global letter_choice
        if letter_choice == 0:
            for k in range(0, size):
                self.str_value += "x" + str(k)
                if self.bin_value[k] == "0":
                    self.str_value += "'"
        elif letter_choice == 1:
            for k in range(0, size):
                self.str_value += chr(97 + k)
                if self.bin_value[k] == "0":
                    self.str_value += "'"
        elif letter_choice == 2:
            for k in range(0, size):
                self.str_value += chr(123 - size + k)
                if self.bin_value[k] == "0":
                    self.str_value += "'"


class Implicant:
    def __init__(self, imp1, imp2=None):
        self.mints = []
        self.dec_value = ""
        self.bin_value = ""
        self.str_value = ""
        self.checked = False

        if type(imp1) == Minterm:
            self.mints.append(imp1)
        elif type(imp1) == Implicant:
            for mint in imp1.mints:
                self.mints.append(mint)

        if imp2 is not None:
            if type(imp2) == Minterm:
                self.mints.append(imp2)
            elif type(imp2) == Implicant:
                for mint in imp2.mints:
                    self.mints.append(mint)

            for i in range(0, len(imp1.bin_value)):
                if imp1.bin_value[i] == imp2.bin_value[i]:
                    self.bin_value += imp1.bin_value[i]
                else:
                    self.bin_value += "-"
        else:
            if type(imp1) == Minterm:
                self.bin_value = imp1.bin_value
        # str_value
        global letter_choice
        if letter_choice == 0:
            for k in range(0, len(self.bin_value)):
                if self.bin_value[k] == "1":
                    self.str_value += "x" + str(k)
                elif self.bin_value[k] == "0":
                    self.str_value += "x" + str(k)
                    self.str_value += "'"
        elif letter_choice == 1:
            for k in range(0, len(self.bin_value)):
                if self.bin_value[k] == "1":
                    self.str_value += chr(97 + k)
                elif self.bin_value[k] == "0":
                    self.str_value += chr(97 + k)
                    self.str_value += "'"
        elif letter_choice == 2:
            for k in range(0, len(self.bin_value)):
                if self.bin_value[k] == "1":
                    self.str_value += chr(123 - len(self.bin_value) + k)
                elif self.bin_value[k] == "0":
                    self.str_value += chr(123 - len(self.bin_value) + k)
                    self.str_value += "'"

        for m in range(0, len(self.mints)):
            self.dec_value += str(self.mints[m].dec_value) + ","
        self.dec_value = self.dec_value[:-1]


class Group:
    def __init__(self, g_name, imp=None):
        self.name = g_name
        self.imps = []
        self.ones = 0
        if imp is not None:
            self.imps.append(imp)
            

class Function:
    def __init__(self, num_of_literals, mints_dec):
        self.literals = num_of_literals
        self.mints = []
        self.groups = []
        self.prime_imps = []
        self.ess_prime_imps = []
        self.optimal_imps = []
        self.expr = ""
        self.optimal_expr = ""
        for m in mints_dec:
            self.mints.append(Minterm(m, num_of_literals))

        for mint in self.mints:
            self.expr += mint.str_value + " + "
            count = 0
            for digit in mint.bin_value:
                if digit == "1":
                    count += 1
            group_name = "G" + str(count)
            if not len(self.groups) == 0:
                found = False
                for group in self.groups:
                    if group.name == group_name:
                        group.imps.append(Implicant(mint))
                        found = True
                if not found:
                    self.groups.append(Group(group_name, Implicant(mint)))
            else:
                self.groups.append(Group(group_name, Implicant(mint)))
        self.expr = self.expr[:-3]

        # should sort groups by increasing number of one
        for group in self.groups:
            group.ones = int(group.name[1:])
        self.groups.sort(key=lambda x: x.ones, reverse=False)

    def combine(self, group1, group2):
        temp_group = Group(group1.name + group2.name)
        for group1_imp in group1.imps:
            for group2_imp in group2.imps:
                if len([i for i in range(self.literals) if group1_imp.bin_value[i] != group2_imp.bin_value[i]]) <= 1:
                    group1_imp.checked = True
                    group2_imp.checked = True
                    temp_group.imps.append(Implicant(group1_imp, group2_imp))

        # should add imp if it is not used in combination
        for imp in group1.imps:
            if not imp.checked:
                temp_group.imps.append(imp)

        # delete duplicate imps
        temp_imps = []
        temp_bin_values = []
        for impl in temp_group.imps:
            temp_imps.append(impl)
            temp_bin_values.append(impl.bin_value)
        temp_bin_values = list(dict.fromkeys(temp_bin_values))
        temp_group.imps.clear()
        for impl in temp_imps:
            if impl.bin_value in temp_bin_values:
                temp_group.imps.append(impl)
                temp_bin_values.remove(impl.bin_value)

        return temp_group

    def solve(self, new_groups):
        count = 0
        for i in range(0, len(new_groups)-1):
            temp_group = self.combine(new_groups[i], new_groups[i+1])
            # when to stop?
            if len(temp_group.imps) == len(new_groups[i].imps):  # prevent out of band exception
                same = True
                for k in range(0, len(temp_group.imps)):
                    if not temp_group.imps[k].bin_value == new_groups[i].imps[k].bin_value:
                        same = False
                        break
                if same:
                    count += 1
            new_groups[i] = temp_group

        # the last group
        last_group = new_groups[len(new_groups)-1]
        temp_last_group = Group(last_group.name)
        for imp in last_group.imps:
            if not imp.checked:
                temp_last_group.imps.append(imp)
        if len(temp_last_group.imps) == 0:  # all imps are combined
            new_groups.remove(last_group)
        else:
            new_groups[len(new_groups)-1] = temp_last_group  # some of the imps are not combined

        # if groups are not combined any more, then stop; else continue
        if not count >= len(new_groups)-1:
            self.solve(new_groups)

    def choose(self, left):
        # choice of max minterms
        max_mints = 0
        for mint in left[0].mints:
            if not mint.covered:  # number of not covered minterms
                max_mints += 1
        for imp in left:
            mints_num = 0
            for mint in imp.mints:
                if not mint.covered:
                    mints_num += 1
            if mints_num > max_mints:
                max_mints = mints_num
        choices = []
        for imp in left:
            mints_num = 0
            for mint in imp.mints:
                if not mint.covered:
                    mints_num += 1
            if mints_num == max_mints:
                choices.append(imp)
        # choice of less literal
        choice = choices[0]
        for imp in choices:
            if imp.bin_value.count('-') > choice.bin_value.count('-'):
                choice = imp
        self.optimal_imps.append(choice)

    def optimize(self):
        if not len(self.groups) == 0:
            self.solve(self.groups)
        for group in self.groups:
            for imp in group.imps:
                self.prime_imps.append(imp)

        for mint in self.mints:
            count = 0
            for prime_imp in self.prime_imps:
                if mint in prime_imp.mints:
                        count += 1
            if count == 1:
                for prime_imp in self.prime_imps:
                    if mint in prime_imp.mints and prime_imp not in self.ess_prime_imps:
                        self.ess_prime_imps.append(prime_imp)

        for imp in self.ess_prime_imps:
            self.optimal_imps.append(imp)  # essentials must be in final expression

        left = []
        while True:
            for imp in self.optimal_imps:
                for mint in imp.mints:
                    mint.covered = True
            for mint in self.mints:
                if not mint.covered:  # if some of minterms are not covered
                    for imp in self.prime_imps:
                        if imp not in self.optimal_imps and mint in imp.mints and imp not in left:
                            left.append(imp)
            if not len(left) == 0:
                self.choose(left)
                left.clear()
            else:
                break

        for imp in self.optimal_imps:
            self.optimal_expr += imp.str_value + " + "
        self.optimal_expr = self.optimal_expr[:-3]

    def print_groups(self):
        for group in self.groups:
            print(5 * "-")
            print(group.name)
            for imp in group.imps:
                print(imp.dec_value, "\t", imp.bin_value, "\t", imp.str_value)


# default values
letter_choice = 5
number_of_literals = 0
mints_list = []

# 0, 1, 2, 5, 7, 8, 9, 10, 13, 15
# 0, 3, 4, 8, 9, 10, 11, 12, 14, 18, 19, 20, 22, 23, 24, 27, 28, 29, 31

"""
for i in range(1, pow(2, number_of_literals)):
    mints_list.append(i)
"""


def get_input():
    global letter_choice, number_of_literals, mints_list
    print(100*"-")
    print("Welcome to Quine-McCluskey Solver Software!")
    print("Choose expression type:")
    print("\t(x0,x1,x2,...) - 0")
    print("\t(a,b,c...) - 1")
    print("\t(x,y,z,...) - 2")
    while True:
        letter_choice = input("Choice: ")
        try:
            letter_choice = int(letter_choice)
            if not 0 <= letter_choice <= 2:
                print("Entered choice ", letter_choice, " is incorrect. Try again.")
            else:
                break
        except ValueError:
            print("Entered choice ", letter_choice, " is incorrect. Try again.")
    while True:
        number_of_literals = input("Enter the number of literals: ")
        try:
            number_of_literals = int(number_of_literals)
            if not 0 < number_of_literals:
                print("Entered value ", number_of_literals, " is incorrect. Try again.")
            else:
                break
        except ValueError:
            print("Entered value ", number_of_literals, " is incorrect. Try again.")
    bad_input = True
    print("Enter minterms list separated by comma (ex.: 0,1,3,5) in range [ 0,", pow(2, number_of_literals)-1, "]:")
    while bad_input:
        mints_input = input().split(",")
        for mint in mints_input:
            try:
                if 0 <= int(mint) <= pow(2, number_of_literals)-1:
                    mints_list.append(int(mint))
                    bad_input = False
                else:
                    print("Entered value ", mint, " is incorrect. Try again.")
                    bad_input = True
                    break
            except ValueError:
                print("Entered value ", mint, " is incorrect. Try again.")
                bad_input = True
                break


def go():
    global number_of_literals, mints_list
    f = Function(number_of_literals, mints_list)
    print(100 * "-")
    print("Initially")
    f.print_groups()

    f.optimize()

    print(100 * "-")
    print("Prime Implicants:")
    max_align = 0
    for imp in f.prime_imps:
        if len(imp.dec_value) > max_align:
            max_align = len(imp.dec_value)
    for imp in f.prime_imps:
        print("\t", imp.dec_value, (max_align-len(imp.dec_value)) * " ", "\t", imp.bin_value, "\t", imp.str_value)
    print(50*"-")
    print("Essential Prime Implicants:")
    for imp in f.ess_prime_imps:
        print("\t", imp.dec_value, (max_align-len(imp.dec_value)) * " ", "\t", imp.bin_value, "\t", imp.str_value)
    print(50 * "-")
    print("Initial form:")
    print("f = ", f.expr)
    print("Optimized form:")
    print("f = ", f.optimal_expr)
    print(100 * "-")


get_input()
go()

