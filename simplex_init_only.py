import numpy as np
from collections import defaultdict

class Simplex:
    def __init__(self, parsed_input, rows=None, c=None):
        if rows != None:
            self.A = parsed_input.A[rows,:]
            self.b = parsed_input.b[rows]
        else:
            self.A = parsed_input.A
            self.b = parsed_input.b
        self.col_dict = parsed_input.col_dict
        self.c = c
        self.B = []
        self.I = []

    def initialization_phase(self):
        if np.all(self.b > 0):
            #print "feasible"
            self.I = np.arange(1+self.A.shape[1]+self.A.shape[0])

            return True
        else:
            (m,n)= self.A.shape
            #print (m, n)
            self.A = np.concatenate((-np.ones((m,1),np.float32), \
                            self.A, np.identity(m,np.float32)),1)
            ind = np.arange(self.A.shape[1])
            B = ind[-m:]
            I = ind[:n+1]
            self.c = np.zeros(1+m+n, np.float32)
            self.c[0] = -1

            # Force x0 to enter
            [B, I, obj, terminal_case] = self.pivot(B, I, True)
            terminal_case = False
            while not terminal_case:
                [B, I, obj, terminal_case] = self.pivot(B,I,False)

            #print 'result', [B, I, obj]
            self.B = B
            self.I = I
            #print 'self',self.I
            #print self.B
            if obj < 0.0:
                #print "infeasible"
                return False;
            else:
                #print "feasible"
                result = self.get_assignment()
                return True

    def solve(self):
        return self.initialization_phase()

    def get_assignment(self):
        result_dict = {}
        (m,n) = self.A.shape
        for i in self.I:
            result_dict[i] = 0
        ind = 0
        for i in self.B:
            Ab = self.A[:,self.B]
            Ai = self.A[:,self.I]
            b_hat = np.linalg.solve(Ab, self.b)
            result_dict[i] = b_hat[ind]
            ind = ind + 1

        result = []
        #print self.I, self.B
        #print result_dict
        for key, val in self.col_dict.iteritems():
            #print key, val
            if val <= n:
                result.append((key, result_dict[val+1]))

        #print 'result', result
        orig_variables = defaultdict(float)
        for ans in result:
            var = ans[0]
            val = ans[1]
            if 'pp' in var:
                var = var.replace('pp', '')
                val *= -1
            else:
                var = var.replace('p', '')
            orig_variables[var] += val
        return orig_variables
        #return result

    def pivot(self, B, I, force_flag):
        Ab = self.A[:,B]
        Ai = self.A[:,I]

        cb = self.c[B]
        ci = self.c[I]

        # pi = Ab \ cb
        pi = np.linalg.solve(np.transpose(Ab), cb)
        obj = np.dot(pi, self.b)

        c_hat = ci - np.dot(pi, Ai)

        #choose enter
        if force_flag:
            enter = 0
        else:
            if (c_hat.max() <= 0):
                #print "done"
                return [B, I, obj, True]
            enter = np.argmax(c_hat)

        b_hat = np.linalg.solve(Ab, self.b)
        a_j_hat = -np.linalg.solve(Ab, self.A[:,I[enter]])

        if force_flag:
            leave = self.b.argmin()
            leavelim = -b_hat[leave] / a_j_hat[leave]
        else:
            #search for leave index
            leave = -1
            leavelim = np.Inf
            for i in np.arange(Ab.shape[0]):
                if a_j_hat[i] < 0:
                    ll = -b_hat[i] / a_j_hat[i]
                    if ll < leavelim:
                        leavelim = ll
                        leave = i

            #leave = (b_hat/ a_j_hat).argmax()
            if leave == -1:
                #print "Unbounded"
                return [B,I, obj, True]


        temp = I[enter]
        I[enter] = B[leave]
        B[leave] = temp

        obj= np.dot(pi, self.b) + c_hat[enter] * leavelim
        return [B, I, obj, False]


'''
A = np.float32([[1,1],[-1,-1]])
b = np.float32([-1, 1-0.001])
'''
'''
# feasible
A = np.float32([[2,-3,7,-15], \
				[0,1,-4,6], \
				[-1,0,1,-2],\
				[0,1,1,0]])
b = np.float32([10,12,4,16])
c = np.float32([1,-1,1,-1])
'''
'''
# feasible
A = np.float32([[-2,1],\
				[0,1],\
				[1,-2],\
				[1,0]])
b = np.float32([-2,4,-2,4])
'''
'''
#infeasible
A = np.float32([[1,-1,0],\
				[0,1,1],\
				[-1,0,1],\
				[0,0,-1]])
b = np.float32([5,14,-6,-7])

rows = [0,1,2,3]
mySimplex = Simplex(A, b, rows)
result = mySimplex.solve()
'''
