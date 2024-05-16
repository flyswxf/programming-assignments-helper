#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int T;
    cin >> T;

    for (int t = 0; t < T; t++)
    {
        int n;
        cin >> n;

        vector<int> a(n);
        for (int i = 0; i < n; i++)
        {
            cin >> a[i];
        }

        vector<int> dp(n, a[0]);
        int maxSum = a[0];

        for (int i = 1; i < n; i++)
        {
            for (int j = 0; j < i; j++)
            {
                if (a[i] > a[j])
                {
                    dp[i] = max(dp[i], dp[j] + a[i]);
                }
            }
            maxSum = max(maxSum, dp[i]);
        }

        cout << "case #" << t << ":" << endl;
        cout << maxSum << endl;
    }

    return 0;
}