from itertools import product
import numpy as np
from csv import writer
from sys import getsizeof
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve


class Station:
    wholesalers = 0
    retailers = 0
    total_stations = 0

    def __init__(self, station_type, name, s, s_max, i, q, d1, d2, m1, m2, l, pos_i_lvl, pos_q_lvl):
        self.station_type = station_type
        self.name = name
        self.s = s
        self.s_max = s_max
        self.i = i
        self.q = q
        self.d1 = d1
        self.d2 = d2
        self.m1 = m1
        self.m2 = m2
        self.l = l
        self.pos_i_lvl = pos_i_lvl
        self.pos_q_lvl = pos_q_lvl

    def user_inputs():
        stations = []

        def get_numeric_input(prompt, desired_type):
            while True:
                try:
                    user_input = input(prompt)
                    if desired_type == int:
                        value = int(user_input)
                    elif desired_type == float:
                        value = float(user_input)
                    else:
                        raise ValueError("Desired type must be int or float")
                    return value

                except ValueError:
                    if desired_type == int:
                        print("Invalid input. Please enter a valid int number")
                    else:
                        print("Invalid input. Please enter a valid float number")

        Station.wholesalers = get_numeric_input(
            "Enter the number of Wholesalers: ", int)
        Station.retailers = get_numeric_input(
            "Enter the number of Retailers ", int)
        Station.total_stations = Station.wholesalers + Station.retailers + 1

        for i in range(Station.total_stations):
            name = ""
            ext_name = ""
            if i == 0:
                name = "Manufacturer"
                ext_name = name
            elif i <= Station.wholesalers:
                name = "Wholesaler"
                ext_name = name + str(i)
            else:
                name = "Retailer"
                ext_name = name + str(i-Station.wholesalers)

            print(
                (f"\nYou have to give input for station {i} Type {name} : \n"))
            s_max = get_numeric_input("Enter s_max (max inv) : ", int)
            s = get_numeric_input("Enter s (reorder point) : ", int)
            d1 = get_numeric_input("Enter d1 : ", float)
            d2 = round(1 - d1, 5)
            m1 = get_numeric_input("Enter m1 : ", float)
            m2 = get_numeric_input("Enter m2 : ", float)

            q = []
            if name == "Retailer":
                l = get_numeric_input(
                    "Enter the external demand rate : ", float)
                for num in range(s+1):
                    if min(s_max - num, stations[Station.wholesalers].s_max) not in q:
                        q.append(
                            min(s_max - num, stations[Station.wholesalers].s_max))
                inv = 0
            elif name == "Manufacturer":
                l = (float(0))

                for num in range(s+1):
                    q.append(s_max-num)
                inv = s_max
            else:
                l = (float(0))
                for num in range(s+1):
                    q.append(min(s_max-num, stations[i-1].s_max))
                inv = 0

            stations.append(Station(name, ext_name, s, s_max,
                            inv, q, d1, d2, m1, m2, l, [], []))
        return (stations)

    def inventory_levels():
        for i in range(Station.wholesalers+1):
            if i == 0:
                # ston Manufacturer ta sigoura inv einai 0, s, s_max....ksekinontas apo s_max tha xtisoume ta alla pithana me vasi to ti tha mas zitisei o epomenos W stathmos
                inv_lvl = [0, stations[i].s_max]

                for q_now in stations[i].q:
                    print(f"q now is : {q_now}")
                    for q_next in stations[i+1].q:
                        inv = inv_lvl[-1]
                        while inv >= 0:
                            if inv > stations[i].s:
                                inv -= min(inv, q_next)
                                if not inv in inv_lvl and inv > 0:
                                    inv_lvl.append(inv)
                            else:
                                if inv + q_now not in inv_lvl and inv + q_now <= stations[i].s_max:
                                    inv += q_now
                                    inv_lvl.append(inv)
                                elif inv - min(inv, q_next) not in inv_lvl:
                                    inv -= min(inv, q_next)
                                else:
                                    break
                            if inv not in inv_lvl:
                                inv_lvl.append(inv)
                            print(f"inv in Manuf is : {inv}")
                        inv_lvl.sort()
                        stations[i].pos_i_lvl = inv_lvl
                for inventory in stations[i].pos_i_lvl:
                    for q_next in stations[i+1].q:
                        if inventory - min(inventory, q_next) not in stations[i].pos_i_lvl and (inventory - min(inventory, q_next)) > 0:
                            stations[i].pos_i_lvl.append(
                                inventory - min(inventory, q_next))
                stations[0].pos_i_lvl.sort()

            else:
                # εδω φτιαχνουμε τα inv lvl των wholesaler+s
                # ξεκιναμε και βάζουμε το 0 και το S_max
                inv_lvl = [0, stations[i].s_max]
                inv = 0
                # κανουμε ενα iterate στο inventory του προηγούμενου σταθμού
                for num in stations[i-1].pos_i_lvl:
                    # εαν το num ειναι μικρότερο απο αυτο που ζητάμε και το num+οτι εχουμε στο inv δν ειναι μεσα, να το βάλουμε
                    for q_now in stations[i].q:
                        if num <= q_now and inv + num not in inv_lvl and inv + num <= stations[i].s_max:
                            inv_lvl.append(inv + num)

                        elif num >= q_now:
                            num = q_now
                            if inv + num not in inv_lvl and inv + num <= stations[i].s_max:
                                inv_lvl.append(inv + num)

                # ξεκιναμε και βάζουμε το 0 και το s μικρό του καθε σταθμού
                # inv_lvl = [0, inventory_policies[i][1]]
                # εδω εχουμε μια λουπα και βλέπουμε που μπορουμε να πάμε ΜΟΝο απο το s μικρό
                for q_now in stations[i].q:
                    inv = stations[i].s
                    # κανουμε ενα iterate στο inventory του προηγούμενου σταθμού
                    for num in stations[i-1].pos_i_lvl:
                        # εαν το num ειναι μικρότερο απο αυτο που ζητάμε και το num+οτι εχουμε στο inv δν ειναι μεσα(ΕΔΩ ΠΡΕΠΕΙ ΝΑ ΜΠΕΙ ΓΙΑ ΟΛΑ ΤΑ ΠΙΘΑΝΑ ΠΟΥ ΕΧΟΥΜΕ), να το βάλουμε
                        if num <= q_now and inv + num not in inv_lvl and inv + num <= stations[i].s_max:
                            inv_lvl.append(inv + num)

                        elif num >= q_now:
                            num = q_now
                            if inv + num not in inv_lvl and inv + num <= stations[i].s_max:
                                inv_lvl.append(inv + num)

                # # ΙΣΩΣ ΔΝ ΥΠΑΡΧΕΙ ΑΝΑΓΚΗ ΓΙΑ ΑΥΤΟ ΤΟ IF
                # if stations[i].q not in inv_lvl:
                #     inv_lvl.append(stations[i].q)

                inv_lvl.sort()

                temp_inv_lvl = inv_lvl

                # !!!!!!!!!!!!!!!!!!!!HOTFIX!!!!!!!!!!!!!!!!!!!!!!
                # LOOP ΓΙΑ ΚΑΘΕ num sto inv του προηγούμενου σταθμού,
                # LOOP για κάθε num στο inv που έχουμε προς το παρόν
                # Εαν προσθέσουμε για κάθε πιθανό inv lvl που έχουμε καθε inv του προηγούμενου
                # KAI δεν το έχουμε ηδη
                # ΚΑΙ ειναι μικρότερο αυτο που μας δίνει απο αυτό που θέλουμε
                # να το βαλουμε και αυτό μέσα
                for num in stations[i-1].pos_i_lvl:
                    # print(
                    #     f"koitame to inv lvl tou {i} σταθμού που ειναι {stations[i-1].pos_i_lvl}")
                    for inv_num in temp_inv_lvl:
                        for q_now in stations[i].q:
                            if num + inv_num not in temp_inv_lvl and num + inv_num <= stations[i].s_max and num <= q_now:
                                inv_lvl.append(inv_num + num)
                            # print(f"HOTFIXED βάλαμε το {inv_num + num}")
                inv_lvl.sort()

                # Eδω ξεκινανε λούπες στην υπαρχον λιστα μας inv_lvl με βάση αυτα που φτιαξαμε με την παραπανω
                if i == Station.wholesalers:
                    # επειδη ειναι ο τελευταιος whole, θα το τρεξουμε για ολους τους Retailers
                    for j in range(Station.wholesalers+1, Station.total_stations):
                        for num in inv_lvl:
                            for q_now in stations[i].q:
                                for q_j in stations[j].q:

                                    inv = num
                                    while inv > 0:
                                        # when we don't need to order
                                        if inv > stations[i].s:
                                            inv -= min(inv, q_j)
                                            if not inv in inv_lvl and inv > 0:
                                                inv_lvl.append(inv)
                                        # when we need an order
                                        else:
                                            if inv + q_now not in inv_lvl and inv + q_now <= stations[i].s_max:
                                                inv += q_now
                                                inv_lvl.append(inv)
                                            else:
                                                inv -= min(inv, q_j)
                                                if inv > 0 and inv not in inv_lvl:
                                                    inv_lvl.append(inv)
                else:
                    for num in inv_lvl:
                        for q_now in stations[i].q:
                            for q_next in stations[i+1].q:
                                inv = num
                                while inv > 0:
                                    # εαν το inv=num ειναι μεγαλύτερο του s, δλδη εαν δεν θελουμε order
                                    if inv > stations[i].s:
                                        # το inv θα μειωθει με βαση το τι θα ζητήσει ο επόμενος
                                        inv -= min(inv, q_next)
                                        if not inv in inv_lvl and inv > 0:
                                            inv_lvl.append(inv)
                                    else:
                                        if inv + q_now not in inv_lvl and inv + q_now <= stations[i].s_max:
                                            inv += q_now
                                            inv_lvl.append(inv)
                                        else:
                                            inv -= min(inv, q_next)
                                            if inv > 0 and inv not in inv_lvl:
                                                inv_lvl.append(inv)
                inv_lvl.sort()
                stations[i].pos_i_lvl = inv_lvl

        for i in range(Station.wholesalers+1, Station.total_stations):
            inv_lvl = []
            for num in range(stations[i].s_max+1):
                if num <= stations[i].s_max:
                    inv_lvl.append(num)
            stations[i].pos_i_lvl = inv_lvl

    # this is a method that creates the real quantity order levels for each station
    # Πρεπει να βαλουμε εξτρα quantity orders, τα οποια ειναι Smax-

    def quantity_order_levels():

        # βάζουμε του Manufacturer τα q level που ειναι 0,q
        # stations[0].pos_q_lvl = [0, stations[0].q[0]]
        stations[0].pos_q_lvl.append(0)
        for q in stations[0].q:
            if q not in stations[0].pos_q_lvl:
                stations[0].pos_q_lvl.append(q)
        for j in range(stations[0].s):
            if stations[0].s_max - j not in stations[0].pos_q_lvl:
                stations[0].pos_q_lvl.append(stations[0].s_max - j)
        stations[0].pos_q_lvl.sort()

        for i in range(1, Station.total_stations):
            q_order_lvl = []
            for quan in stations[i].q:
                if i <= Station.wholesalers:
                    for num in stations[i-1].pos_i_lvl:
                        if num <= quan:
                            q_order_lvl.append(num)
                        else:
                            q_order_lvl.append(quan)
                else:
                    for num in stations[Station.wholesalers].pos_i_lvl:
                        if num <= quan:
                            q_order_lvl.append(num)
                        # προσθεσα αυτο το ελσε, που για καποιον λογο δν υπήρχε
                        else:
                            q_order_lvl.append(quan)
            temp_q_order_lvl = []
            [temp_q_order_lvl.append(x)
             for x in q_order_lvl if x not in temp_q_order_lvl]
            q_order_lvl = temp_q_order_lvl
            q_order_lvl.sort()
            stations[i].pos_q_lvl = q_order_lvl

    def system_info():
        log_to_file_and_terminal("\n \n ")
        for stat in stations:
            log_to_file_and_terminal(
                f"Station type: {stat.station_type} with name {stat.name} has inventory_policy ({stat.s_max}, {stat.s}) inventory policy and  q order size = {stat.q},")
            log_to_file_and_terminal(
                f"Also it's  d1= {stat.d1} d2= {stat.d2}  m1= {stat.m1}  m2= {stat.m2}  l= {stat.l} and his poss inv_lvl is {stat.pos_i_lvl} and his poss q_lvl is {stat.pos_q_lvl}\n")


def real_states():
    # Δημιουργει ολους τους δυνατους συνδιασμους που υπαρχουν χωρις να περασει απο περιορισμους
    def kartesian_product():
        print('\nGenerating kartesian product\n')
        product_list = []
        for i in range(Station.total_stations):
            # Το καθε ψηφιο ειναι μια μεταβλητη, #1=inventory level #2=quantity_order #3=state of pending order
            product_list.append(stations[i].pos_i_lvl)
            product_list.append(stations[i].pos_q_lvl)
            product_list.append(range(3))
        poss_states = product(*product_list)
        print('End of kartesian product\n')

        return poss_states

    # Φιλτραρει την καθε πιθανη κατασταση και επιστρεφει Τrue αν περασει τους ελεγχους μας και False αν οχι
    def restrictions(p):
        # DN GINETAI na theloume paragelia kai na pairnoume megalytero apo oti exoume anagi
        for i in range(Station.total_stations):
            if p[3*i] <= stations[i].s and (p[3*i+1]+p[3*i]) > stations[i].s_max:
                return False
        # Ο Manufacturer dexete ola ta pithana q pou zitaei
        if p[0] <= stations[0].s and (p[1] not in stations[0].q or p[2] == 0):
            return False
    # An o M dn thelei order, dn ginete j!=0 kai q != 0
        if p[0] > stations[0].s and (p[1] != 0 or p[2] != 0):
            return False
        for i in range(1, Station.wholesalers+1):
            # an o Station i thelei order kai dn perimenei hdh, dn ginete o -1 stathmos na exei inventory !=0
            if p[3*i] <= stations[i].s and p[3*i+1] == 0 and p[3*(i-1)] != 0:
                return False
            # An o Station i den thelei order tote dn ginete q+j na einai != 0
            if p[3*i] > stations[i].s and (p[3*i+1] != 0 or p[3*i+2] != 0):
                return False
            # An o station i perimenei order dn ginete to j na einai 0
            if p[3*i+1] != 0 and p[3*i+2] == 0:
                return False
            # An j !=0 dn ginete to q = 0
            if p[3*i+2] != 0 and p[3*i+1] == 0:
                return False

        for i in range(1+Station.wholesalers, Station.total_stations):
            # an o retailer i thelei order kai dn perimenei hdh, dn ginete o last Whole na exei inv != 0
            if p[3*i] <= stations[i].s and p[3*i+1] == 0 and p[3*Station.wholesalers] != 0:
                return False
            # An o Retailer i thelei order tote dn ginete q+j na einai != 0
            if p[3*i] > stations[i].s and (p[3*i+1] != 0 or p[3*i+2] != 0):
                return False
            # ao o retailer i periemnei order dn ginete to j na einai 0
            if p[3*i+1] != 0 and p[3*i+2] == 0:
                return False
            # An j !=0 dn ginete to q = 0
            if p[3*i+2] != 0 and p[3*i+1] == 0:
                return False
        return True

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!SOLUTION 2!!!!!!!!!!!!!!!!!!!!!!!!!!
    # filtered_states = (state for state in kartesian_product() if restrictions(state))
    # states = list(filtered_states)

    poss_states = kartesian_product()

    states = []
    print(
        '\nYpologismos restrictions, kratame mono tis katastaseis pou theloume \n')
    for p in poss_states:
        #    print( f' Checking state {p} ')
        if restrictions(p):
            # state = make_str(p)
            states.append(p)
            # print(p)
    #    else:
    #        rejected += 1

    print('\nRestrictions TELOS!!!\n')

    # log_to_file_and_terminal(f"The # of rejected states is : {rejected}")
    log_to_file_and_terminal(f"The # of real states is : {len(states)}\n")
    return states


# it takes the state in tuple state and returns it in readable way
def make_str(tup):
    name = ""
    i = 0
    for char in tup:
        if i % 3 == 0:
            name += " "
        name += str(char)+" "
        i += 1
    return name


def steady_state_propabilities():
    def filling_trans_matrix():
        print('\nStarting filling trans matrix........ \n')
        # Initiate τον πινακα με ζερος.........................
        i = len(make_str(states[0]))
        transition_matrix = np.zeros(
            (len(states), len(states)), dtype=np.single)

        # Indexing απο 0 μεχρι μέγεθος πίνακα
        for i in range(len(states)):
            # state_st είναι τι θα βαλουμε στην κατασταση που μενουμε
            state_st = int()
            # state_to ειναι τι θα βαλουμε στην κατασταση στην οποια θα παμε
            state_to = int()
            # state_temp ειναι η κατασταση που βρισκομαστε αλλα τι κανουμε temp για να την διαχειριστουμε
            # state_temp = list
            state_temp = list(states[i])
            # σαρωση s index απο 0 μεχρι πόσους σταθμούς έχουμε (εξεταζουμε μια μια τις τριαδες αριθμων)

            for s in range(Station.total_stations):
                # Πως μενουμε ιδια κατασταση ανεξαρτητως που ειμαστε, αρα γεμιζουμε κυρια διαγωνιο
                # Αν j=1 πως μενουμε ιδια κατάσταση
                if states[i][3*s+2] == 1:
                    state_st += - 1 * (stations[s].m1)
                # Αν j=2 πως μενουμε ιδια κατάσταση
                elif states[i][3*s+2] == 2:
                    state_st += - 1 * (stations[s].m2)
                # Αν ο retailer εχει αποθεμα , πως δεν μας το παιρνει ο καταναλωτης (-λ)
                if s >= Station.wholesalers+1 and states[i][3*s] != 0:
                    state_st += - 1 * (stations[s].l)
                # Αποθηκευση καταστασης  στην κυρια διαγωνιο
                transition_matrix[i, i] = state_st

                # Πως αλλαζουμε κατασταση απο j=1 σε j=2.............................................................................................................
                if states[i][3*s+2] == 1:
                    # Κανουμε save την κατάσταση μας στην temp μεταβλητη
                    state_temp = list(states[i])
                    # Αντικατάσταση j=1 σε j=2
                    state_temp[3*s+2] = 2
                    # Βρισκουμε την ιδια κατασταση  με j=2 αντι j=1 και παμε εκει και βαζουμε την τιμη της
                    state_temp = tuple(state_temp)
                    found_i = states.index(state_temp)
                    state_to = 0
                    state_to += (stations[s].d2) * (stations[s].m1)
                    transition_matrix[i, found_i] = state_to

                # Πως εξυπηρετουμε πελάτες ?
                if s > Station.wholesalers:
                    state_temp = list(states[i])
                    if state_temp[3*s] > 0:
                        state_cust = 0
                        state_cust += (stations[s].l)
                        state_temp[3*s] -= 1
                        # //////////////////////////////////////////////////
                        for num in range(Station.total_stations-1, -1, -1):
                            # κοιτάμε αν θελουμε order και δεν περιμενουμε ηδη και αν μπορει να μας δώσει ο προηγουμενος, και κανουμε ετσι update προς τα πισω
                            if state_temp[3*num] <= stations[num].s and state_temp[3*num+2] == 0:
                                # Αν ειμαστε στον Manufacturer παιρνουμε "free" ΄ότι ζητήσουμε
                                if num == 0:
                                    # Το q του Manufacturer γινεται q
                                    state_temp[3*num+1] = stations[num].s_max - \
                                        state_temp[3*num]
                                    # To j απο 0 γίνεται 1
                                    state_temp[3*num+2] = 1

                                # Αν ειμαστε στους Wholesalers κοιταμε τον προηγόυμενο σταθμο αν μπορει να μας δωσει αυτο που θέλουμε
                                elif num <= Station.wholesalers:
                                    # Κοιταμε τον προηγουμενο αν εχει να μας δωσει απο το inventory του,!
                                    if state_temp[3*(num-1)] > 0:
                                        # το j του σταθμού μας θα γίνει 1
                                        state_temp[3*num+2] = 1
                                        # το q του σταθμού μας θα γίνει ότι μας δώσει/θέλουμε
                                        state_temp[3*num+1] = min(
                                            # state_temp[3*(num-1)], stations[num].q)
                                            state_temp[3*(num-1)], (stations[num].s_max - state_temp[3*num]))
                                        # o προηγουμενος σταθμος θα χασει αυτο που θα μας δωσει
                                        q_lost = state_temp[3*num+1]
                                        state_temp[3*(num-1)] -= q_lost

                                # Ειμαστε στους Retailers , εδώ κοιτάμε τον Last Whole
                                else:
                                    if state_temp[3*Station.wholesalers] > 0:
                                        # το j του σταθμού μας θα γίνει 1
                                        state_temp[3*num+2] = 1
                                        # το q του σταθμού μας θα γίνει ότι μας δώσει/θέλουμε !!!!!!!!!!!!!!!!!!!!!!!ΣΟΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣ!!!!!!!!!!!!!!!!!!!!!
                                        state_temp[3*num+1] = min(
                                            # state_temp[3*Station.wholesalers], stations[num].q)
                                            state_temp[3*Station.wholesalers], (stations[num].s_max - state_temp[3*num]))

                                        # o wholesaler ο τελευταιος  θα χασει αυτο που θα μας δωσει
                                        q_lost = state_temp[3*num+1]
                                        state_temp[3 *
                                                   Station.wholesalers] -= q_lost

                        state_temp = tuple(state_temp)
                        found_i = states.index(state_temp)
                        transition_matrix[i, found_i] = state_cust

                # Πως εξυπηρετουμε απο j=1 ή j=2..........................................................................................................................
                if states[i][3*s+2] == 1 or states[i][3*s+2] == 2:
                    # Αποθηκευση του quantity order μας σε μια temp τιμη .
                    q_temp = states[i][3*s+1]
                    # Θετουμε μεταβλητη q_give = 0 , που ειναι τι θα δωσουμε
                    q_give = 0
                    # Κανουμε save την κατάσταση μας σε μια temp μεταβλητη οπου θα μπορουμε να την πειραζουμε μεχρι να δουμε που θα φτασει
                    state_temp = list(states[i])
                    # Κανουμε adjust τιμες j q i απο την στιγμη που ερχεται παραγγελια
                    state_temp[3*s] += q_temp
                    state_temp[3*s+1] = 0
                    state_temp[3*s+2] = 0
                    # Αν την θέλει ο επόμενος σταθμός και δεν περιμένει ήδη, θα την πάρει ! ΙΣΧΥΕΙ ΜΕΧΡΙ ΚΑΙ ΠΡΟΤΕΛΕΥΤΑΙΟ Whole, μετα αλλαζει
                    if s < Station.wholesalers:
                        if state_temp[3*(s+1)+2] == 0 and state_temp[3*(s+1)] <= stations[s+1].s:
                            # το q που θα πάρει, θα είναι το ελάχιστο από  **τι inventory έχουμε  και αυτό που μας ζητάει
                            # q_give = min(state_temp[3*s],
                            #              stations[s+1].q)
                            q_give = min(state_temp[3*s],
                                         (stations[s+1].s_max - state_temp[3*(s+1)]))
                            # Ο επόμενος σταθμός παίρνει  q=q_give και το j από 0 γίνεται 1 και εμεις χαναουμε αυτο που δωσαμε
                            state_temp[3*(s+1)+1] = q_give
                            state_temp[3*(s+1)+2] = 1
                            state_temp[3*s] -= q_give

                    # ειμαστε στον τελευταιο Wholesaler , αρα δινουμε σε ολους τους δυνατους Retailers  με σειρα προτεραιοτητας
                    elif s == Station.wholesalers:
                        i_temp = True
                        s_temp = Station.wholesalers + 1
                        while i_temp and s_temp < Station.total_stations:
                            if state_temp[3*s_temp+2] == 0 and state_temp[3*s_temp] <= stations[s_temp].s:
                                # το q που θα πάρει, θα είναι το ελάχιστο από  τι inventory έχουμε + αυτό που ζητάει
                                # q_give = min(state_temp[3*s],
                                #              stations[s_temp].q)
                                q_give = min(state_temp[3*s],
                                             stations[s_temp].s_max - state_temp[3*s_temp])
                                # Ο επόμενος σταθμός παίρνει  q=q_give και το j από 0 γίνεται 1 και εμεις χανουμε αυτο που δωσαμε
                                state_temp[3*s_temp+1] = q_give
                                state_temp[3*s_temp+2] = 1
                                state_temp[3*s] -= q_give
                                i_temp = False
                            # Αν ο επόμενος δέν θέλει/περιμένει παραγγελία
                            else:
                                s_temp += 1

                    # #Εμείς μένουμε στο inventory με ότι εχουμε - ότι δώσαμε
                    # state_temp[3*s] -= q_give
                    # Κοιταμε αν θέλουμε παραγγελία, αν μπορούμε να πάρουμε και μετα κανουμε adjusts τι επηρρεαζει ολο αυτο
                    # Κοιταμε αν θέλουμε παραγγελια
                    if state_temp[3*s] <= stations[s].s:
                        # Αν ειμαστε στον Manufacturer παιρνουμε "free" ΄ότι ζητήσουμε
                        if s == 0:
                            # Το q του Manufacturer γινεται oso θελει να παρει
                            state_temp[3*s+1] = stations[s].s_max - \
                                state_temp[3*s]
                            # To j απο 0 γίνεται 1
                            state_temp[3*s+2] = 1
                        # Αν ειμαστε στους Wholesalers κοιταμε τον προηγόυμενο σταθμο αν μπορει να μας δωσει αυτο που θέλουμε
                        elif s <= Station.wholesalers:
                            # Κοιταμε τον προηγουμενο αν εχει να μας δωσει απο το inventory του,!
                            if state_temp[3*(s-1)] > 0:
                                # το j του σταθμού μας θα γίνει 1
                                state_temp[3*s+2] = 1
                                # το q του σταθμού μας θα γίνει ότι μας δώσει/θέλουμε !!!!!!!!!!!!!!!!!!!!!!!ΣΟΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣ!!!!!!!!!!!!!!!!!!!!!
                                # state_temp[3*s+1] = min(state_temp[3*(s-1)],
                                #                         stations[s].q)
                                state_temp[3*s+1] = min(state_temp[3*(s-1)],
                                                        (stations[s].s_max - state_temp[3*s]))
                                # o προηγουμενος σταθμος θα χασει αυτο που θα μας δωσει
                                q_lost = state_temp[3*s+1]
                                state_temp[3*(s-1)] -= q_lost
                        # Ειμαστε στους Retailers , εδώ κοιτάμε τον Last Whole
                        else:
                            if state_temp[3*Station.wholesalers] > 0:
                                # το j του σταθμού μας θα γίνει 1
                                state_temp[3*s+2] = 1
                                # το q του σταθμού μας θα γίνει ότι μας δώσει/θέλουμε !!!!!!!!!!!!!!!!!!!!!!!ΣΟΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣ!!!!!!!!!!!!!!!!!!!!!
                                # state_temp[3*s+1] = min(state_temp[3 *
                                #                         Station.wholesalers], stations[s].q)
                                state_temp[3*s+1] = min(state_temp[3 *
                                                        Station.wholesalers], stations[s].s_max - state_temp[3*s])
                                # o wholesaler ο τελευταιος  θα χασει αυτο που θα μας δωσει
                                q_lost = state_temp[3*s+1]
                                state_temp[3*Station.wholesalers] -= q_lost
                    # Πρεπει να κανουμε μια λουπα που θα στελνει τα μετεωρα κομματια που προεκυψαν απο τα παρε-δωσε σε οποιον τα θελει,
                    # θα πρεπει να ξεκιναει απο τερμα δεξια και να πηγαινει τερμα αριστερα.
                    # Λογικα μετα το shorting η κατασταση που θα εχει μεινει θα ειναι και η πραγματικη
                    for num in range(Station.total_stations-1, -1, -1):
                        # κοιτάμε αν θελουμε order και δεν περιμενουμε ηδη και αν μπορει να μας δώσει ο προηγουμενος, και κανουμε ετσι update προς τα πισω
                        if state_temp[3*num] <= stations[num].s and state_temp[3*num+2] == 0:
                            # Αν ειμαστε στον Manufacturer παιρνουμε "free" ΄ότι ζητήσουμε
                            if num == 0:
                                # Το q του Manufacturer γινεται q
                                state_temp[3*num+1] = stations[num].s_max - \
                                    state_temp[3*num]
                                # To j απο 0 γίνεται 1
                                state_temp[3*num+2] = 1
                            # Αν ειμαστε στους Wholesalers κοιταμε τον προηγόυμενο σταθμο αν μπορει να μας δωσει αυτο που θέλουμε
                            elif num <= Station.wholesalers:
                                # Κοιταμε τον προηγουμενο αν εχει να μας δωσει απο το inventory του,!
                                if state_temp[3*(num-1)] > 0:
                                    # το j του σταθμού μας θα γίνει 1
                                    state_temp[3*num+2] = 1
                                    # το q του σταθμού μας θα γίνει ότι μας δώσει/θέλουμε
                                    # state_temp[3*num+1] = min(
                                    #     state_temp[3*(num-1)], stations[num].q)
                                    state_temp[3*num+1] = min(
                                        state_temp[3*(num-1)], (stations[num].s_max - state_temp[3*num]))

                                    # o προηγουμενος σταθμος θα χασει αυτο που θα μας δωσει
                                    q_lost = state_temp[3*num+1]
                                    state_temp[3*(num-1)] -= q_lost
                            # Ειμαστε στους Retailers , εδώ κοιτάμε τον Last Whole
                            else:
                                if state_temp[3*Station.wholesalers] > 0:
                                    # το j του σταθμού μας θα γίνει 1
                                    state_temp[3*num+2] = 1
                                    # το q του σταθμού μας θα γίνει ότι μας δώσει/θέλουμε !!!!!!!!!!!!!!!!!!!!!!!ΣΟΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣΣ!!!!!!!!!!!!!!!!!!!!!
                                    # state_temp[3*num+1] = min(
                                    #     state_temp[3*Station.wholesalers], stations[num].q)
                                    state_temp[3*num+1] = min(
                                        state_temp[3*Station.wholesalers], stations[num].s_max - state_temp[3*num])
                                    # o wholesaler ο τελευταιος  θα χασει αυτο που θα μας δωσει
                                    q_lost = state_temp[3*num+1]
                                    state_temp[3*Station.wholesalers] -= q_lost
                    state_temp = tuple(state_temp)
                    # print(
                    #     f'Eimaste sthn katastasi {make_str(states[i])} kai pame sthn katastash {state_temp}')
                    found_i = states.index(state_temp)
                    state_to = 0
                    if states[i][3*s+2] == 1:
                        state_to += (stations[s].d1) * (stations[s].m1)
                    elif states[i][3*s+2] == 2:
                        state_to += (stations[s].m2)
                    transition_matrix[i, found_i] = state_to
        print('\nFilling trans matrix is over. \n')
        # np.savetxt("test_dip.csv", transition_matrix,delimiter=",")
        return transition_matrix

    transition_matrix = filling_trans_matrix()

    info(transition_matrix, "Transition Matrix")

    p_matrix = transition_matrix
    for i in range(0, len(states)):
        p_matrix[i, -1] = 1

    b_matrix = np.zeros((len(states), 1), dtype=np.single)
    b_matrix[-1] = 1

    p_trans = np.transpose(p_matrix)

    sparse_p_trans = csc_matrix(p_trans)
    x_matrix = spsolve(sparse_p_trans, b_matrix)

    info(x_matrix, "Steady-State Matrix")

    sum_x = np.sum(x_matrix)

    # Normalize x_matrix by dividing each element by the sum
    x_matrix_normalized = x_matrix / sum_x

    # Στρογγυλοποιήστε τον πίνακα στα # δεκαδικά ψηφία
    x_matrix_rounded = np.round(x_matrix_normalized, decimals=6)
    print(f"the sum of steady stade matrix is {sum(x_matrix_rounded)}")
    # whole_inv = np.zeros(20)
    # for i in range(len(states)):
    #     for num in range(20):
    #         if states[i][3] == num:
    #             whole_inv[num] += x_matrix_rounded[i]
    # print(f'THE WHOLESALER STATIONARY PROP IS :')
    # for num in whole_inv:
    #     print(num)

    return (x_matrix_rounded)


def info(matrix, matrix_name="Matrix"):
    memory_usage_bytes = getsizeof(matrix)
    memory_usage_gb = memory_usage_bytes / (1024 * 1024 * 1024)
    log_to_file_and_terminal(
        f"{matrix_name} - Shape: {matrix.shape}, Memory Usage: {memory_usage_gb:.2f} GB \n")


def perfomance_measures():
    fr_retailers = []
    wip_in_transit = []
    wip_on_hand = []
    wip_system = []

    for s in range(0, Station.total_stations):
        sum_fr = 0
        sum_fr_b = 1
        sum_wip_in_transit = 0
        sum_wip_on_hand = 0
        for i in range(len(states)):
            # FR retailer i
            if s > Station.wholesalers:
                if states[i][3*s] != 0:
                    sum_fr += steady_state_prop[i]
                else:
                    sum_fr_b -= steady_state_prop[i]

            # WIP in transit i station
            if states[i][3*s+2] != 0:
                sum_wip_in_transit += (states[i][3*s+1] * steady_state_prop[i])
            # WIP ON HAND
            if states[i][3*s] != 0:
                sum_wip_on_hand += (states[i][3*s] * steady_state_prop[i])

        wip_on_hand.append(sum_wip_on_hand)
        wip_in_transit.append(sum_wip_in_transit)
        fr_retailers.append(sum_fr)
        wip_system.append(sum_wip_in_transit + sum_wip_on_hand)

    # OLA AYTA PREPEI NA MPOUNE STO CLASS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for i in range(0, Station.total_stations):
        if i > Station.wholesalers:
            log_to_file_and_terminal(
                f"FR tou {stations[i].name} is {fr_retailers[i]}")
        log_to_file_and_terminal(
            f"Wip in transit tou {stations[i].name} einai {wip_in_transit[i]}")
        log_to_file_and_terminal(
            f"Wip on hand tou {stations[i].name} einai: {wip_on_hand[i]}\n")

    total_fr = 0
    total_wip_in_transit = 0
    total_wip_on_hand = 0
    total_wip_system = 0
    for num in fr_retailers:
        total_fr += num
    for num in wip_in_transit:
        total_wip_in_transit += num
    for num in wip_on_hand:
        total_wip_on_hand += num
    for num in wip_system:
        total_wip_system += num

    thr = 0
    for i in range(Station.wholesalers+1, Station.total_stations):
        thr += fr_retailers[i] * stations[i].l

    log_to_file_and_terminal(f"\nTotal FR is : {total_fr}\n")
    log_to_file_and_terminal(f"Total wip on hand is : {total_wip_on_hand}\n")
    log_to_file_and_terminal(
        f"Total wip in transit is : {total_wip_in_transit}\n")
    log_to_file_and_terminal(f"Total Wip for system is : {total_wip_system}\n")
    log_to_file_and_terminal(f"THR for retailers is : {thr}\n")

    log_to_file_and_terminal(f"fr_retailers is {fr_retailers}")


def log_to_file_and_terminal(message, filename_prefix="log"):
    print(message)
    # # Generate a filename with a timestamp

    finelame_sufix = f'M({stations[0].s_max}-{stations[0].s})'
    for i in range(1, Station.total_stations):
        if stations[i].station_type == 'Wholesaler':
            finelame_sufix += f' W({stations[i].s_max}-{stations[i].s})'
        else:
            finelame_sufix += f' R({stations[i].s_max}-{stations[i].s})'

    filename = f"{filename_prefix} {finelame_sufix}.txt"

    # Save the message to a text files
    with open(filename, "a") as file:
        file.write(message + "\n")


#!!!!!!!!!!!!!  MAIN CODE !!!!!!!!!!!!!!!!!!!!
stations = Station.user_inputs()

Station.inventory_levels()

Station.quantity_order_levels()

Station.system_info()

states = real_states()

steady_state_prop = steady_state_propabilities()

perfomance_measures()
