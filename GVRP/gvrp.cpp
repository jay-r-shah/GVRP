#include <ilcplex/ilocplex.h>
#include <math.h>
ILOSTLBEGIN

bool checkExistence(IloNumArray array, int val);

int main(int argc, char **argv) {
	IloEnv env;
	try {
		IloInt m = 4;
		IloInt Q = 15;
		string formulation = "node";
		float maxTime = 2*60*60;
		float objLim = 0;

		string filename = "GVRP";
		string filepath =  "../../data/" + filename + ".dat"; 
		if (argc >= 2) filepath = argv[1];
		ifstream file(filepath);
		if(!file) {
			cerr << "No such file: " << filename << endl;
			throw(-1);
		}
		IloNumArray2 xy(env), V(env), c(env);
		IloNumArray q(env);
		IloModel mod(env);

		file >> xy >> V;
		IloInt nCustomers = xy.getSize();
		IloInt nClusters = V.getSize();
		for (int i = 0; i < nClusters; ++i)
		{
			q.add(V[i].getSize());
		}
		q[0] = 0;

		for (int i = 0; i < nCustomers; ++i)
		{
			IloNumArray rowdist(env);
			for (int j = 0; j < nCustomers; ++j)
			{
				rowdist.add(sqrt(pow(xy[i][0] - xy[j][0] , 2) + pow(xy[i][1] - xy[j][1] , 2)));
			}
			c.add(rowdist);
		}

		// Variables
		typedef IloArray<IloNumVarArray> NumVarMatrix;
		typedef IloArray<IloBoolVarArray> BoolVarMatrix;
		BoolVarMatrix x(env, nCustomers);

		for(int i = 0; i < nCustomers; i++){
			x[i] = IloBoolVarArray(env, nCustomers);
		}

		NumVarMatrix w(env, nClusters);
		for(int i = 0; i < nClusters; i++){
			w[i] = IloNumVarArray(env, nClusters, 0,IloInfinity, ILOFLOAT);
		}

		// Objective 

		IloExpr TotalCost(env);
		for (int i = 0; i < nCustomers; ++i)
		{
			for (int j = 0; j < nCustomers; ++j)
			{
				TotalCost += c[i][j] * x[i][j];
			}
		}
		mod.add(IloMinimize(env, TotalCost));
		TotalCost.end();

		// Objective Limit
		IloExpr TotalCost2(env);
		for (int i = 0; i < nCustomers; ++i)
		{
			for (int j = 0; j < nCustomers; ++j)
			{
				TotalCost2 += c[i][j] * x[i][j];
			}
		}
		mod.add(TotalCost2 >= objLim);
		TotalCost2.end();

		// Set x[i][i] == 0
		for (int i = 0; i < nCustomers; ++i)
		{
			IloExpr dummy2(env);
			dummy2 += x[i][i];
			mod.add(dummy2 == 0);
			dummy2.end();
		}

		// eliminate arcs within clusters:

		for (int p = 1; p < nClusters; ++p)
		{
			for (int count_i = 0; count_i < V[p].getSize(); ++count_i)
			{
				for (int count_j = 0; count_j < V[p].getSize(); ++count_j)
				{
					if (count_i != count_j)
					{
						int i = V[p][count_i];int j = V[p][count_j];
						mod.add(x[i][j] == 0);
					}
				}
			}
		}


		// Constraint 1
		for (int p = 1; p < nClusters; ++p)
		{
			IloExpr ClusterDegree(env);
			for (int count_i = 0; count_i < V[p].getSize(); ++count_i)
			{
				int i = V[p][count_i];
				for (int j = 0; j < nCustomers; ++j)
				{
					if (!checkExistence(V[p],j))
					{
						ClusterDegree += x[i][j];
					}
				}
			}
			mod.add(ClusterDegree == 1);
			ClusterDegree.end();
		}

		// Constraint 2
		for (int p = 1; p < nClusters; ++p)
		{
			IloExpr ClusterDegree2(env);
			for (int i = 0; i < nCustomers; ++i)
			{
				if (!checkExistence(V[p],i))
				{
					for (int count_j = 0; count_j < V[p].getSize(); ++count_j)
					{
						int j = V[p][count_j];
						ClusterDegree2 += x[i][j];
					}
				}
			}
			mod.add(ClusterDegree2 == 1);
			ClusterDegree2.end();
		}

		// Constraint 3
		IloExpr ClusterDegree3(env);
		for (int i = 1; i < nCustomers; ++i)
		{
			ClusterDegree3 += x[0][i];
		}
		mod.add(ClusterDegree3 <= m);
		ClusterDegree3.end();
		
		// Constraint 4
		IloExpr ClusterDegree4(env);
		for (int i = 1; i < nCustomers; ++i)
		{
			ClusterDegree4 += x[i][0];	
		}
		mod.add(ClusterDegree4 <= m);
		ClusterDegree4.end();

		// Constraint 5
		for (int p = 0; p < nClusters; ++p)
		{
			for (int count_j = 0; count_j < V[p].getSize(); ++count_j)
			{
				IloExpr Connectivity(env);
				int j = V[p][count_j];
				for (int i = 0; i < nCustomers; ++i)
				{
					if (!checkExistence(V[p],i))
					{
						Connectivity += x[i][j];
					}
				}
				for (int i = 0; i < nCustomers; ++i)
				{
					if (!checkExistence(V[p],i))
					{
						Connectivity += -x[j][i];
					}
				}
			mod.add(Connectivity == 0);
			Connectivity.end();
			}
		}

		// Constraint 6
		for (int p = 0; p < nClusters; ++p)
		{
			for (int r = 0; r < nClusters; ++r)
			{
				IloExpr Connectivity2(env);
				Connectivity2 += w[p][r];
				if (p!=r)
				{
					for (int count_i = 0; count_i < V[p].getSize(); ++count_i)
					{
						int i = V[p][count_i];
						for (int count_j = 0; count_j < V[r].getSize(); ++count_j)
						{
							int j = V[r][count_j];
							Connectivity2 += -x[i][j];
						}
					}
				}
				mod.add(Connectivity2 == 0);
				Connectivity2.end();
			}
		}

		/*Node based formulation:*/
		IloNumVarArray u(env);
		for (int p = 0; p < nClusters; ++p)
		{
			u.add(IloNumVar(env,0.0, Q, ILOFLOAT));
		}

		// Constraint 9
		for (int p = 1; p < nClusters; ++p)
		{
			IloExpr cBounding(env);
			cBounding += u[p] - q[p];
			for (int r = 0; r < nClusters; ++r)
			{
				if (r!=p)
				{
					cBounding += - q[r] * w[r][p];
				}
			}
			mod.add(cBounding >= 0);
			cBounding.end();
		}


		// Constraint 10
		for (int p = 1; p < nClusters; ++p)
		{
			IloExpr cBounding2(env);
			cBounding2 += u[p] + (Q- q[p])*w[0][p] - Q;

			mod.add(cBounding2 <= 0);
			cBounding2.end();
		}

		// Constraint 11
		for (int p = 1; p < nClusters; ++p)
		{
			IloExpr cBounding3(env);
			cBounding3 += u[p] - Q;
			for (int r = 0; r < nClusters; ++r)
			{
				if (r != p)
				{
					cBounding3 += q[r] * w[p][r];
				}
			}
			mod.add(cBounding3 <= 0);
			cBounding3.end();
		}

		// Constraint 12
		for (int p = 1; p < nClusters; ++p)
		{
			for (int r = 1; r < nClusters; ++r)
		 	{
		 		if (p!=r)
		 		{
		 			IloExpr subtour(env);
		 			subtour += u[p] - u[r] + Q*w[p][r] + (Q - q[p] - q[r]) * w[r][p] - Q + q[r];
		 			mod.add(subtour <= 0);
		 			subtour.end();
		 		}
		 	}
		 }

		int NUM_THREADS = 4;
		IloCplex cplex(mod);
		cplex.setParam(IloCplex::Param::TimeLimit, maxTime);
		cplex.setParam(IloCplex::Param::Threads, NUM_THREADS);
		IloNum timebef = cplex.getTime();
		bool foundFeasibleSolution = cplex.solve();
		float runtime = double((cplex.getTime() - timebef)/NUM_THREADS);
		env.out() << "Solution Status: " << cplex.getStatus() << endl;
		env.out() << endl << "Total Cost = " << cplex.getObjValue() << endl;
		env.out() << "Number of constraints: " << cplex.getNrows() << endl;
		env.out() << "Nodes: " << cplex.getNnodes() << endl;
		env.out() << "Run time: " << runtime << endl;

		string resultsFilename;
		resultsFilename += "../../results/"+filename+"_node_" + to_string(nCustomers) + "_" + to_string(nClusters) + "_" +  to_string(m)+ "_";
		if (objLim > 0)
		{
			int valObj = floor(objLim);
			resultsFilename += "OL" + to_string(valObj) + "_";
		}
		int valTime = floor(maxTime/60);
		resultsFilename += "TL" + to_string(valTime) + ".txt";
		cout << "Results printed to :" << resultsFilename << endl; 
		ofstream fout(resultsFilename, ios::out);
		fout <<"Sol ";
		fout << "GVRP with " << to_string(nCustomers - 1) << " customers and " << to_string(m) << " vehicles" << endl;
		for (int i = 0; i < nCustomers; ++i)
		{
			for (int j = 0; j < nCustomers; ++j)
			{
				if (cplex.getValue(x[i][j]) > 0.9)
				{
					fout << i << " " << j << " " << endl;
				}
			}
		}
		fout << "Cost " << cplex.getObjValue() << endl;
		fout << "DataFile " << filename;
		fout.close();

		ofstream logfile;
		string logFileName = "GVRPLogFile";
		logfile.open("../../"+logFileName+".txt",std::ios_base::app);
		logfile << "NODE "<< filename << " OBJ " << cplex.getObjValue() << " RUNTIME " << runtime << " RELGAP " << cplex.getMIPRelativeGap();
		logfile << " nCust " << nCustomers << " nClusters " << nClusters << " nVehicles "<< m << " nRows " << cplex.getNrows();
		logfile <<  " TIMELIM " << maxTime << " OBJLIM " << objLim << endl;
		cout << "Log file: " << logFileName << endl;
	}
	catch (IloException& ex) {
      cerr << "Error: " << ex << endl;
   }
   catch (...) {
      cerr << "Error: Unknown exception caught!" << endl;
   }

   env.end();

   return 0;
}

bool checkExistence(IloNumArray array, int val) {
	for (int i = 0; i < array.getSize(); ++i)
	{
		if (array[i] == val)
		{
			return 1;
		}
	}
	return 0;
}