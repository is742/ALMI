# -*- coding: utf-8 -*-
import heapq, random, glob, subprocess
import numpy as np
from copy import deepcopy
import numpy as np
from random import randint, uniform

# =============================================================================
# Environment Creation Interface
# =============================================================================
''' The environment creates an interface for the entity which stores information 
    relating to the entities interpretation of the environment. The graph class 
    also creates all connections and maps for the environment, and includes path
    finding using Dijkstra's algorithm.    
'''
class Graph:
    def __init__(self, n_nodes, ID, n_probs=3):
        # Setup nodes and variables
        self.n_nodes = n_nodes  # Number of nodes in the environment
        self.n_probs = n_probs  # Number of probabilities (success, fail, return)
        self.dist_array = np.zeros(shape=(n_nodes, n_nodes))
        self.prob_array = np.zeros(shape=(n_nodes, n_nodes))
        self.map = dict()       # Default environment map
        self.heat_map = dict()  # Adjusted heatmap.
        self.ID = ID
        self.connections = None # Map connections        

        # Variables for information.
        self.path = None
        self.paths = self.__Path()
        
        # Initilise the dynamics of the agent (technically... kinematics)
        self.dynamics = self.__Dynamics()
        
        # Task Specific Variables 
        self.mission = self.__Mission()
                
    # =============================================================================
    # Create Connections and Add Connections
    # -----------------------------------------------------------------------------
    # The Create_Connection method takes in a list of connections between two nodes 
    # and adds the connection to the distance and probability arrays.
    # =============================================================================
    def Create_Connections(self, connections):
        # Create connections between the nodes
        for c in connections:
            node_1 = c[0]
            node_2 = c[1]
            distance = c[2]
            probability = c[3]
            
            # Update the value in the distance array for the first node and the 
            # second node. This should also be repeated as the array should be 
            # mirrored about the diagonal.
            self.dist_array[node_1-1, node_2-1] = distance
            self.dist_array[node_2-1, node_1-1] = distance
            
            # We may have a second input which requires use of the probability array
            # If this is the case, populate that array in the same manner as the previous
            # distance array.
            if probability is not None:
                self.prob_array[node_1-1, node_2-1] = probability
                self.prob_array[node_2-1, node_1-1] = probability

        # Since the default connections only exist as one edge per node connection, create 
        # the reversal to complete every single edge within the map.
        self.connections =  [x for x in connections]
        for i in range(len(self.connections)):
            # Take the edge and reverse the first two entries. 
            edge = [x for x in self.connections[i]]
            edge[0], edge[1] = edge[1], edge[0]
            self.connections.append(edge)

    # =============================================================================
    # Create Map
    # -----------------------------------------------------------------------------
    # Create the environment map based on the probability and distance matrices 
    # which were populated using the Create_Connections method. 
    #
    # A map can also be created from a previously defined map. This helps eliminate
    # stochastic behaviour when creating the map, since many variables are randomly
    # computed, no two maps will ever be the same.
    # =============================================================================
    def Create_Map(self, env_map=None):
        # The input variable env_map allows this instance to be created based on 
        # a previously created map. However, if this value is None, we should create 
        # the map from scratch. 
        if env_map is None:
            # When creating the connections between each node, the connections are 
            # defined with two values: distance and probabilty. However, only the 
            # distance value is required with the probability optional. Therefore, 
            # we need to check to make sure we have information within the probability 
            # array in order to use that information to populate the values. Therefore, 
            # we should check to see if the probabiltiy array has been populated by 
            # checking its maximum value. If the array has values, the maximum value 
            # will be greater than zero, which was the default.
            if self.prob_array.max() > 0:
                # Create the map using information from the distance and probabilty 
                # matrices.
                for i in range(self.dist_array.shape[0]):
                    self.map[i+1] = dict()
                    for j in range(self.dist_array.shape[1]):
                        if self.dist_array[i,j] != 0:
                            prob_success = self.prob_array[i,j] # Obtain the prob of success
                            
                            # Generate random probabilities based on the probability of success 
                            # using the internal method __Random_Probabilities. This returns 
                            # three variables, a fail, a return state and a total value. The
                            # total value should always equal 1. 
                            prob_fail, prob_return, total = self.__Random_Probabilities(prob_success)
            
                            
                            # For some scenarios where we have a probability of success,
                            # the value which corresponds a failure may not have a return state, 
                            # meaning if the state fails, there is no second changes. This is 
                            # determined based on the number of probabilities assigned to the class
                            # when it is created. For example, if the number  of probs is 2,
                            # then the return probability should be zero and it's value added onto 
                            # the failure probability.
                            if self.n_probs == 2:
                                prob_fail += prob_return
                                prob_return = 0
                            
                            # Create a map strucutre based on the nodes i and j and create a 
                            # dictionary of values corresponding to the probabilities/ 
                            self.map[i+1][j+1] = {"Distance"    : self.dist_array[i,j],
                                                  "Success"     : prob_success,
                                                  "Return"      : prob_return,
                                                  "Fail"        : prob_fail,
                                                  "Total"       : total}
            
            # The probabilty array indicates  it has not been populated and therefore
            # we should create the map using only the distance array. This is mainly 
            # used for population of maps where probabilty values are not important 
            # or do not exist, such as when creating maps for humans which do not have 
            # probabilities of success defined. 
            else:
                # Create the map using information from ONLY the distance 
                for i in range(self.dist_array.shape[0]):
                    self.map[i+1] = dict()
                    for j in range(self.dist_array.shape[1]):
                        if self.dist_array[i,j] != 0:
                            self.map[i+1][j+1] = {"Distance" : self.dist_array[i,j]}
        
        # If the env_map variable is NOT None, then we should create this instance 
        # from a previously defined map.                     
        else:
            # Crate a deep copy of the map to prevent values being known based on 
            # memory addresses. 
            self.map = deepcopy(env_map)
            
            # If the map which was created does not have the same number of probabilities
            # that are equal to 3, then we need to adjust the probabilities. 
            if self.n_probs == 2:
                # We should add the "return" probability to the "fail" probability, and
                # reset the "return" probabilty to zero as it won't be used. 
                for node in self.map:
                    for conn in self.map[node]:
                        self.map[node][conn]['Fail'] = np.round(self.map[node][conn]["Fail"] + self.map[node][conn]['Return'], 2)
                        self.map[node][conn]['Return'] = 0
                        
    # =============================================================================
    # Create Random Probabilities for Environment Map
    # -----------------------------------------------------------------------------
    # This is an internal method for creating the environment map based on the dist 
    # and probability arrays. It uses the probability of success to create a randomly 
    # generated return and failure state, which when added together with the success 
    # value MUST equal one. 
    # =============================================================================
    def __Random_Probabilities(self, success):
        total = 0 # Create initial total for checking the value inside the while statement
        catch = 0 # Catch to prevent unlimited re-tries due to dec_place inconsistencies.

        # We cannot exit the function if the total value is NOT 1.
        while total != 1.00:
            # We need to first find the decimal place to allow a better represenation 
            # of the number of places we must determine the values for. For example, 
            # if the success if 0.4, then the fail states are comprised of 0.6, with
            # one decimal place. However, if the success is 0.95, the fail state need 
            # to be must smaaller and defined quantities within the round function, as
            # they must be comprised of only 0.05. 
            dec_place = str(success)[::-1].find('.')
            dec_place += 2 # Apply a larger offset for higher resolution.   

            # Using the success value, determine the maximum value used to create 
            # the returna and failure states. 
            remainder = np.round(1 - success, dec_place)
            
            # Create one ranndom value using a uniform distribution and apply the 
            # decimal place derived before for accuracy. 
            val_1 = 0 #random.uniform(remainder*0.1, remainder)
            val_1 = np.round(val_1 * 0.1, dec_place) # this scales the value to force the fail state to be much smaller

            
            # Determine the second value by subtracing the first random value from the 
            # remainder. 
            val_2 = np.round(remainder - val_1, dec_place)
    
            # Ideally, we want the return prob to be larger than the fail prob. Therefore
            # use a simple if statement to catch the larger number and then assign the 
            # final states values. 
            if val_1 >= val_2:
                ret = val_1
                fail = val_2
            else:
                ret = val_2 
                fail = val_1
            
            # Add the probabilities to ensure they add up to one
            total = success + fail + ret
            
        # If we break out of the loop, return the values as outputs from the 
        # function. We also return the total value as a check for later. 
        return fail, ret, total
       

    # =============================================================================
    # Create Random Missions
    # -----------------------------------------------------------------------------
    # This method creates random missions for the agent based on the following 
    # parameters:
    #   1: n_nodes       - defines the number of tasks within the mission
    #   2: phase_rate    - defines the probability of a task being ordered, creating 
    #                       a new phase
    #   3: max_unordered - defines the number of consecutive unordered tasks in any 
    #                      phase. This value should ideally not be set higher than 5
    #                      as this creates unnecessarily large permutations. 
    #   4: human_rate    - defines the probability that a task will be allocated to
    #                      the human to perform
    #   5: max_human     - defines the maximum number of tasks which can be 
    #                      allocated to the human. This value is set by default to 0
    #                      to prevent tasks being allocated in the event we do not 
    #                      have a human.
    # =============================================================================
    def Random_Mission(self, n_nodes, phase_rate=0.8, max_unordered=5, human_rate=None, max_human=0):
        min_node = min(self.map)
        max_node = max(self.map)
    
        self.dynamics.position = randint(min_node, max_node)    # Creates a random start location for the agent
        self.mission.start = self.dynamics.position             # Updates the start of the mission 
        self.mission.tasks = [randint(min_node, max_node) for i in range(n_nodes)]  # randomly compute tasks
        u_counter = 0
        h_counter = 0

        # Create the headers for the mission 
        self.mission.headers = list()
        for i in range(n_nodes-1):  # Iterate until one node from end... final node is O
            # To prevent large unordered tasks from accumulating, use 
            # the max_unordered variable to limit the number of consecutive 
            # unordered tasks.
            if u_counter < max_unordered:
                if uniform(0, 1) <= phase_rate:
                    # If the task is set to be un-ordered, it can be applied
                    # for the human to perform.
                    if (uniform(0, 1) <= human_rate) and (h_counter < max_human):
                        self.mission.headers.append("H") # Apply to human
                        h_counter += 1
                    else:
                        self.mission.headers.append("U") # Apply to agent
                    u_counter += 1 # Add to the counter
                else:
                    self.mission.headers.append("O") # Apply as ordered to agent
                    u_counter = 0 # Reset the counter
            else:
                self.mission.headers.append("O")
                u_counter = 0 # Reset the counter

        # Make the last index a hold statement 
        self.mission.headers.append("O")

    # =============================================================================
    # Update heat map    
    # -----------------------------------------------------------------------------
    # If a path is created for one entity, this path can be used to adjust the prob
    # of success in another entities map by applying a scaling factor to nodes within 
    # the path.
    #   1. human_path: predicted path for the human 
    #   2. human_position: current position of the human 
    #   3. scale1: scaling functionapplied when the edge has a dual conflict
    #   4. scale2: scaling function applied when the edge has a single conflict
    # =============================================================================
    def Update_Heat(self, human, scale1=0.5, scale2=0.90):
        human_path = human.paths.selected.path
        human_position = human.dynamics.position

        # Create a heat map based on the default map.
        self.heat_map = deepcopy(self.map)
        inv_scale1 = 1 - scale1
        inv_scale2 = 1 - scale2

        # Determine which connections should be adjusted based on the path.
        # Iterate through each connection...
        for c in self.connections:
            # If both connections are in the path for the human, apply the harsher scale function
            if (c[0] in human_path) and (c[1] in human_path):
                success_scale =  np.round(self.heat_map[c[0]][c[1]]["Success"] * scale1, 5)  # Scale the success probability
                remainder = np.round(self.heat_map[c[0]][c[1]]["Success"] * inv_scale1, 5)   # Calculate the remainder
                partition = np.round(remainder / 3, 5) # Scale the remainder to apply as return and fail offsets

                self.heat_map[c[0]][c[1]]["Success"] = success_scale # Update the success prob for first edge
                self.heat_map[c[0]][c[1]]["Return"] += partition*2   # Update the return state
                self.heat_map[c[0]][c[1]]["Fail"] += partition       # Update the fail state
                
            # If only a single connection is in the path for the human, apply a reduced scale function
            elif (c[0] in human_path) or (c[1] in human_path):
                success_scale =  np.round(self.heat_map[c[0]][c[1]]["Success"] * scale2, 5)  # Scale the success probability
                remainder = np.round(self.heat_map[c[0]][c[1]]["Success"] * inv_scale2, 5)    # Calculate the remainder
                partition = np.round(remainder / 3, 5) # Scale the remainder to apply as return and fail offsets

                self.heat_map[c[0]][c[1]]["Success"] = success_scale # Update the success prob for first edge
                self.heat_map[c[0]][c[1]]["Return"] += partition*2   # Update the return state
                self.heat_map[c[0]][c[1]]["Fail"] += partition       # Update the fail state
            
            # If the position of the human is located at a node, we cannot move to that node
            # and if we are located at that node, we should NOT move from it and just hold 
            # position by setting the return statement to be 1
            if c[0] == human_position or c[1] == human_position:
                self.heat_map[c[0]][c[1]]["Success"] = 0 # Set the success to 0
                self.heat_map[c[0]][c[1]]["Return"] = 1  # Set the return to 1
                self.heat_map[c[0]][c[1]]["Fail"] = 0    # Set the fail state to 0

            # Similarly, if a node is located along the next node for the predicted human's path, 
            # we should never attempt to go to it, so set the return statement to 1 and we will 
            # hold position. 
            elif c[0] == human_path[0] or c[1] == human_path[1]:
                self.heat_map[c[0]][c[1]]["Success"] = 0 # Set the success to 0
                self.heat_map[c[0]][c[1]]["Return"] = 1  # Set the return to 1
                self.heat_map[c[0]][c[1]]["Fail"] = 0    # Set the fail state to 0


    # =============================================================================
    # Dijkstra's Algorithm for Path Finding
    # =============================================================================
    def Dijkstra(self, start, final, path_class=None, method="Distance", secondary="Success", map=None):       
        # We want to be able to use updated heatmaps, so if the map variable is None, use the default map, 
        # else, set the map to be the map passed into the method. 
        if map is None:
            map = self.map  # Set the map to be the default map

        if method == "Distance":
            # We are using Dijkstra's algorithm to minimise distance.
            nodes = {k : np.inf for k in map.keys()}
            nodes[start] = 0 # Set the edge we are starting at to the be min value.
            prev_node = dict()
            
            # create connection list and use heapq priorty queue
            connections = list()
            heapq.heappush(connections, (0, start))
            # While we have a node in the heap
            while connections:
                # obtain the current lowest distance in the heap array
                curr_distance, curr_node = heapq.heappop(connections)
                
                # Iterate through each neighbour at the current node location
                # for neighbour, edge_dist in self.map[curr_node].items():
                for connection in map[curr_node].items():
                    # the connection variable will return a list with two values:
                    #  - the connecting neighbour
                    #  - and the values of distance, success.... etc within the map for this neighbour
                    neighbour = connection[0]
                    edge = connection[1]["Distance"]
                    
                    # Calculate the new distance using the current distance and the distance 
                    # to the neighbour
                    new_distance = curr_distance + edge 
            
                    # If the new distannce is less than the known distance to that neighbour... update its value.
                    if new_distance < nodes[neighbour]:
                        nodes[neighbour] = new_distance # Update the distance to the node
                        prev_node[neighbour] = curr_node # store the previous neighbour for backtracking the path.
                        
                        # push the connection for the current distance and neighbour
                        heapq.heappush(connections, (new_distance, neighbour))
        
        elif method == "Probability":
            # We are using Dijkstra's to maximise probability.
            nodes = {k : 0 for k in map.keys()}
            nodes[start] = 1 # Set the edge we are starting at to the maximum expected value.
            prev_node = dict()
            
            # create connection list and use heapq priorty queue
            connections = list()
            heapq.heappush(connections, (0, start))
            
            # While we have a node in the heap
            while connections: 
                # obtain the current lowest 
                curr_prob, curr_node = heapq.heappop(connections)
                
                # Iterate through each neighbour at the current node location
                # for neighbour, edge_dist in self.map[curr_node].items():
                for connection in map[curr_node].items():
                    # the connection variable will return a list with two values:
                    #  - the connecting neighbour
                    #  - and the values of distance, success.... etc within the map for this neighbour
                    neighbour = connection[0]
                    edge = connection[1]["Success"]# + connection[1]["Return"]

                    # If the success of moving across an edge is 0, this means a path 
                    # should not be created for this node. However, if this is a one-way 
                    # route, and there is no alternative, we should still allow a path to 
                    # be created, albeit with a very-very poor chance of success. Therefore, 
                    # set the edge to be very small if this occurs.
                    if edge == 0:
                        edge = 0.05

                    # calculate the new probability to the neighbour
                    if curr_prob == 0:
                        new_probability = edge
                    else:
                        new_probability = curr_prob * edge
    
                    # If the new probability is less than the known probability to that neighbour, update its value
                    if new_probability > nodes[neighbour]:
                        nodes[neighbour] = new_probability
                        prev_node[neighbour] = curr_node
                        
            
                        # Push the connection for the current probability and neighbour 
                        heapq.heappush(connections, (new_probability, neighbour))
        
        # If the input method was not recognised.
        else:
            print("Optional methods are: 'Distance' or 'Probability'")
            
        
        # Create the path
        path_position = final
        path = [path_position]
        
        # To create the path we need to traverse the predecessor locations from 
        # the final position to the start location.
        while path_position is not start:
            next_position = prev_node[path_position]
            path.append(next_position)
            path_position = next_position
        path.reverse() # Since the path will be backwards, we need to reverse the path
        
        # Now we have a path, we should also return the value of the opposite method. 
        # So if we used distance, we should determine the probability of the path. 
        if method == "Distance":
            probability = 1
            for i in range(len(path)-1):
                x_1 = path[i]
                x_2 = path[i+1]
                probability *= (map[x_1][x_2]["Success"] + map[x_1][x_2]["Return"])
            distance = nodes[final]
        
        elif method == "Probability":
            distance = 0
            for i in range(len(path)-1):
                x_1 = path[i]
                x_2 = path[i+1]
                distance += map[x_1][x_2]["Distance"]
            probability = nodes[final]
            
        # The method input has a "path_class" which indicates a map has been 
        # applied for which the path solution can been appended to.
        if path_class is not None:
            # Create the exportation for the class.
            path_class.path = path
            path_class.length = distance
            path_class.prob = probability
            path_class.valid = None # Reset the validation value.
            return self
        
        # The method does not have a class to update the values in. Therefore, 
        # we will return the raw values for the path, distance and probability.
        else: 
            return path, distance, probability
    
    # =============================================================================
    #  Method for validating a created path using the PRISM class.
    # -----------------------------------------------------------------------------
    # When creating a path using Dijkstra's algorithm, the algorithm only considers 
    # the path which has the highest chance of success, immediately, and does not 
    # consider the fact that a path has a return state, allowing the agent to try
    # the edge again. For this reason, PRISM is used to validate the probability of
    # successfully reaching the end state in a systematic way. For these reasons, 
    # the probabilty of success obtained through PRISM is usually larger than that 
    # returned using Dijkstra. 
    # =============================================================================
    def Validate_Path(self, prism_path, path):
        
        # To validate the path using PRISM we need to create the appropriate 
        # actions for the PRISM model using the created path.
        action = Prism.Generate_Action(self.map, num_solutions=1, initial_guess=path)
        
        # Generate PRISM code and compile the PRISM model.
        code = Prism.Create_Model(self.map, self.position, path[-1], action[0,:])
        file_path, model_name = Prism.Export_Model(code, file_name="Model_1.prism")
        
        # Run the PRISM model and obtain the validation value from the PCTL.
        validation = Prism.Simulate(prism_path, file_path+model_name, output_files=True)
        
        
        return validation

    # =============================================================================
    # Compile Mission
    # -----------------------------------------------------------------------------
    # When the task breakdown has been created, the mission can be applied to the 
    # agent class by compiling inside this methodology. This will create the 
    # necessary information for the mission inside the agent's class.
    # =============================================================================
    def Compile_Mission(self, sub_tasks):
        # Update the mission breakdown 
        self.mission.breakdown = deepcopy(sub_tasks)

        # Set the phase information 
        self.mission.n_phase = len(sub_tasks)   # Determine number of phases 
        self.mission.i_phase = 1                # Set the current phase index to 1
        self.mission.c_phase = True             # Set the complete phase bool to False

        self.mission.i_task = 1
        self.mission.t_task = 0

    # =============================================================================
    # Environment Print History Method
    # -----------------------------------------------------------------------------
    # Use this method to print specific instances of the simulation.
    # =============================================================================
    def Print(self, data, step_number):
        for i in data[step_number][self.ID.lower()]:
            string = str(data[step_number][self.ID.lower()][i])
            print("%-30s %-30s" % (i, string))

    # =============================================================================
    # Sub-Class for Environment Paths
    # -----------------------------------------------------------------------------
    # This sub-class creates the path class that is applied to the agent for 
    # navigation throught the environment. It cannot be called externally by the 
    # class through methods, and is initalised during creation.
    #
    # The purpose of this class is to create a set of initialised variables for 
    # simulation, such as the selected path and the parameters (distance/prob) 
    # for the selected path.
    # =============================================================================
    class __Path: 
        def __init__(self):
            self.selected = self.__Instance()       # Selected path for simulated
            self.max_prob = self.__Instance()       # Path created using Dijkstra (probability)
            self.min_dist = self.__Instance()       # Path created using Dijkstra (distance)
            # self.history = np.empty(shape=(0,2))    # Historic path information for the agent
            self.history = list()
            
        class __Instance:
            def __init__(self):
                self.path = None            # Actual path 
                self.i_path = 0             # Current position (index) along the path
                self.n_return = 0           # Counter for return states
                self.length = None          # Distance of the path
                self.prob = None            # Probability of completing the path (Dijkstra)
                self.time = None            # Time expected to complete the path 
                self.valid = None           # Validation probability from Prism.
                self.dist_cum = None        # Iterative cummulative distance of the path.
                self.off_path = False       # Boolean for determining if the entity has moved off path

    # =============================================================================
    # Sub-Class for Environment Tasks 
    # -----------------------------------------------------------------------------
    # The sub-class Task initialises the task for the agent governed by the main 
    # Mission class. 
    #
    # Each mission is comprised of a series of tasks where each task is represented 
    # by a location within the environment. Since tasks do not necessary have to be 
    # conducted in sequantial order, tasks are assigned headers which are characters 
    # that describe whether the task is an ordered or un-ordered process.
    # =============================================================================
    class __Mission: 
        def __init__(self):
            self.start = None       # Start location for the agent.
            self.tasks = None       # List of tasks as node locations
            self.phase = None       # What is the current phase task list?!
            self.n_phase = 0     # Number of phases in a mission
            self.i_phase = 0     # Current phase index in the mission
            self.i_task  = 0     # Current task index in a specific phase
            self.t_task = 0      # Total tasks completed
            self.c_phase = None  # Boolean for whether the current phase is complete
            self.events = 0      # Number of events

            self.breakdown = None   # Full mission breakdown

            self.index = 0          # Index of the sub-mission
            self.progress = None    # Progress of the task by the agent
            self.position = 0       # Position of the task? 
            self.complete = False   # List of completed tasks
            self.failed = False     # Boolean for whether the mission failed.
            self.mission = None     # When the mission order has been selected... it goes here! 
            self.time = 0           # Timer for mission progress
            self.n_stuck = 0        # Counter for number of return states.

            # Each task is comprised of a series of locations defined by nodes 
            # within the environment. Each task is assigned a header which defines 
            # its characteristics for completion. 
            # Headers: C ("Check"), H ("Hold")
            self.headers = None
            
     
    # =============================================================================
    # Agent Dynamics
    # -----------------------------------------------------------------------------
    # This class sets the dynamics of the agent during simulation
    # =============================================================================
    class __Dynamics:
        def __init__(self):
            self.velocity = 0.5     # transitional velocity (m/s)
            self.rotation = 0.5     # angular velocity (rad/s)
            self.position = None    # Position of the agent (node position)
            self.yaw      = 0.0     # Yaw angle of the agent (rad)

            ''' History = [ mission sub-task, 
                            Phase,
                            Task index for phase,
                            position index on path,
                            curr_pos, 
                            next_pos, 
                            act_pos, 
                            p_succ, 
                            p_ret, 
                            p_fail,
                            uniform]
            
            '''
            self.history  = np.empty(shape=(0, 11))
            self.history_columns = ['Task ID', 'Phase', 'Phase Task', 'Path Index', 'Current Position', 'Next Waypoint', 'Actual Next Position', 'P_Succ', 'P_Ret', 'P_fail', 'Value']



























