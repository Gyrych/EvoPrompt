#include <stdio.h>

//感知器结构：
//
//	in1----(w1)----\
//	              求和----硬限幅器----out
//  in2----(w2)----/         |(theta)
//	                        -1

typedef struct
{
	float w1;		//感知器输入in1的权重
	float w2;		//感知器输入in2的权重
	float theta;	//硬限幅器的阀值
} PERCEPTRONPARAMETER;	//感知器参数表类型

void init_perceptron(PERCEPTRONPARAMETER* parameter);					//初始化感知器,		输入：参数表源地址;
int perceptron(float in1, float in2, PERCEPTRONPARAMETER parameter);	//计算感知器输出，	输入：in1，in2，参数表;
void training_perceptron(float in1[], float in2[], float out[], int num, float alfa, PERCEPTRONPARAMETER* parameter);	//训练感知器，输入：训练集in1，训练集in2，训练集out，训练集样本数，学习速度（小于1），参数表源地址;

#define SAMPLESIZE 10	//样本数
float ex_in1[SAMPLESIZE] = { 0,  4, 6, 7.5,    8,  8.2,    9,    15, 100.45, 2000};	//训练样本
float ex_in2[SAMPLESIZE] = {-0.001, 10, 2, 3.7, 8.99, 5.68, 1.07, 200.8,    190,  140};
float ex_out[SAMPLESIZE] = { 1,  0, 1,   1,    0,    1,    1,     0,      0,    1};

int main(void)
{

	PERCEPTRONPARAMETER p;	//感知器参数表
	float in1,in2,out;		//感知器输入输出

	init_perceptron(&p);	//初始化参数表
	printf("\n感知器训练前参数： w1: %g, w2: %g, theta: %g\n", p.w1, p.w2, p.theta);
	training_perceptron(ex_in1, ex_in2, ex_out, SAMPLESIZE, 0.1, &p);	//训练感知器
	printf("感知器训练后参数： w1: %g, w2: %g, theta: %g\n", p.w1, p.w2, p.theta);
	while(1)
	{
		printf("\n感知器输入in1： ");
		scanf("%f", &in1);
		printf("感知器输入in2： ");
		scanf("%f", &in2);
		out = perceptron(in1, in2, p);
		printf("感知器输出： %g\n\n", out);
	}

	return 0;
}

void init_perceptron(PERCEPTRONPARAMETER* parameter)	//初始化感知器
{
	parameter->w1 = 0;		//初始化in1权重w1
	parameter->w2 = 0;		//初始化in2权重w2
	parameter->theta = 0;	//初始化硬限幅器阀值
}

int perceptron(float in1, float in2, PERCEPTRONPARAMETER parameter)	//感知器运算
{															//输入1,输入2,参数表
	float input = 0;

	input = in1 * parameter.w1 + in2 * parameter.w2;		//计算硬限幅器输入
	if(input >= parameter.theta)							//硬限幅器运算
		return 1;
	else
		return 0;
}

void training_perceptron(float in1[], float in2[], float out[], int num, float alfa, PERCEPTRONPARAMETER* parameter)	//感知器训练
{
	float error = 0, deltaw1 = 0, deltaw2 = 0, deltatheta = 0;
	int i = 0, j = 0;

	while(j < 1000)
	{
		for(i = 0; i < num; i++)
		{
			error = out[i] - perceptron(in1[i], in2[i], *parameter);

			deltaw1 = alfa * in1[i] * error;
			deltaw2 = alfa * in2[i] * error;
			deltatheta = alfa * (-1) * error;

			parameter->w1 = parameter->w1 + deltaw1;
			parameter->w2 = parameter->w2 + deltaw2;
			parameter->theta = parameter->theta + deltatheta;
		}
		j++;
	}
}

