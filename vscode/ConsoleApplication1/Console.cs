//using Microsoft.Office.Interop.Excel;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;


namespace ConsoleApplication1
{
    public class Console
    {
        public static void Main(string[] args)
        {
            //train(1000, 10);

            //train(3, 4);
        }

        public static bool train(int epoch, int batch)
        {

            int count = 0;
            int action_runtime = 180 * 5;
            int state_runtime = 180 * 5;
            string outputPath = "./outputs";

            List<string> errors = new List<string>();
            List<string> records = new List<string>();

            //Initialize all the instances
            ShAgent agent = new ShAgent();
            VissimTools.InitVissimTools();
            VissimTools.vissimRunFirstInterval();
            for (int e = 0; e < epoch; e++)
            {
                var watch = System.Diagnostics.Stopwatch.StartNew();

                int batch_count = 0;
                double batch_diff = 0;

                for (int b = 0; b < batch; b++)
                {
                    //get initial state from vissim to agent

                    double raw_state = VissimTools.vissimState(count, state_runtime); // TBD:

                    // map to discrete  
                    if (raw_state < agent.get_min_state() || raw_state > agent.get_max_state())
                    {
                        count++;
                        continue;
                    }

                    batch_count++;

                    int state = (int)((raw_state - agent.get_min_state()) / agent.state_interval);

                    // temp store of current q table for convergence check
                    double[,] current_q_table = agent.q_table.Clone() as double[,];

                    // get action
                    List<int> action = agent.get_action(state);

                    // get reward

                    int limSpd = (int)(agent.get_min_action() + action[0] * agent.action_interval);
                    double reward = VissimTools.vissimReward(action_runtime, limSpd);

                    // update q table
                    agent.update_q_table(state, action[0], reward);

                    /*
                    Application app = new Application { Visible = false };
                    Workbook xBook = app.Workbooks._Open(@"D:\School11111111111111111111111111111\Coop2019\Summer\Capacity\Data\data.xlsx");
                    Worksheet xSheet = (Worksheet)xBook.Sheets[1];
                    Range c1 = (Range)app.Cells[count * 13 + 1, 1];
                    Range c2 = (Range)app.Cells[count * 13 + 1 + 13 - 1, 10];
                    Range range = app.get_Range(c1, c2);
                    range.Value = agent.q_table;
                    xBook.Save();
                    xSheet = null;
                    xBook.Close(0); //xlBook.Close(true); //Workbook.close(SaveChanges, filename, routeworkbook )
                    app.Quit();
                    */

                    double diff = 0;
                    count++;

                    diff += Math.Abs(agent.q_table[state, action[0]] - current_q_table[state, action[0]]);
                    /*
                    for (int m = 0; m < agent.get_state_size(); m++)
                    {
                        for (int n = 0; n < agent.get_action_size(); n++)
                        {
                            diff += Math.Abs(agent.q_table[m, n] - current_q_table[m, n]);
                        }
                    }
                    */

                    System.Console.WriteLine("Run #:" + count + " ----------- " + diff + " (" + state + " : " + action[0] + " : " + action[1] + ")");

                    records.Add(count + "," + diff + "," + state + "," + action[0] + "," + action[1] + "," + reward);

                    batch_diff += diff;

                    GC.Collect();
                }
                // TBD: check if this is a good check

                double error = batch_diff / batch_count;
                errors.Add(error + "");

                System.Console.WriteLine("Error: ================== >" + error);

                if ((batch_diff / batch_count) < agent.convergence)
                {
                    summary(records, outputPath, "final_outputs.csv");
                    summary(errors, outputPath, "final_error_outputs.csv");
                    save_q(agent.q_table, "final");

                    return true;
                }

                watch.Stop();

                System.Console.WriteLine("Epoch " + e + " execution time: ========== >" + watch.ElapsedMilliseconds);

                summary(records, outputPath, "temp_outputs_epoch_" + e + ".csv");
                summary(errors, outputPath, "temp_error_outputs_epoch_" + e + ".csv");
                save_q(agent.q_table, e + "");

                GC.Collect();
            }
            return true;
        }

        public static void summary(List<string> data, string outputPath, string fileName)
        {
            StreamWriter fileWriter = new StreamWriter(Path.Combine(outputPath, fileName));

            foreach (string line in data)
                fileWriter.WriteLine(line);

            fileWriter.Close();
        }

        public static void save_q(double[,] q_table, string fileName)
        {
            StreamWriter fileWriter = new StreamWriter(@"./outputs/q_table_" + fileName + ".csv");

            for (int s = 0; s < q_table.GetLength(0); s++)
            {
                string content = "";
                for (int a = 0; a < q_table.GetLength(1); a++)
                {
                    content += q_table[s, a].ToString();

                    if (a != q_table.GetLength(1) - 1)
                    {
                        content += ",";
                    }
                }
                //trying to write data to csv
                fileWriter.WriteLine(content);
            }
            fileWriter.Close();
        }
    }

}






