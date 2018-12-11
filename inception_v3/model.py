import tensorflow as tf
from cnn_helpers import average_gradients, make_fc, make_dropout
from cnn_helpers import make_batch_norm, make_relu, make_flatten
from cnn_helpers import make_conv_no_bias, make_conv_1x1_no_bias
from cnn_helpers import make_conv_3x3_no_bias, make_conv_3x3_stride_2_no_bias
from cnn_helpers import make_conv_3x1_no_bias, make_conv_1x3_no_bias
from cnn_helpers import make_conv_5x5_no_bias
from cnn_helpers import make_conv_1x7_no_bias, make_conv_7x1_no_bias
from cnn_helpers import make_avg_pool, make_avg_pool_3x3
from cnn_helpers import make_max_pool_3x3, make_avg_pool_5x5_stride_3
from inception_v3.lsr_loss import lsr_loss


def make_tower(tower_name, x_in, y_out, keep_prob, is_training, count_classes):
    ############################################################################
    intnsr = x_in
    scope  = tower_name+"/input_stem"
    ############################################################################

    conv1  = make_conv_3x3_stride_2_no_bias("conv1", scope, intnsr, 32)
    bn1    = make_batch_norm("bn1", scope, conv1, is_training)
    relu1  = make_relu("relu1", scope, bn1)

    conv2  = make_conv_3x3_no_bias("conv2", scope, relu1, 32)
    bn2    = make_batch_norm("bn2", scope, conv2, is_training)
    relu2  = make_relu("relu2", scope, bn2)

    conv3  = make_conv_3x3_no_bias("conv3", scope, relu2, 64, padding="SAME")
    bn3    = make_batch_norm("bn3", scope, conv3, is_training)
    relu3  = make_relu("relu3", scope, bn3)
    pool3  = make_max_pool_3x3("pool3", scope, relu3)

    conv4  = make_conv_1x1_no_bias("conv4", scope, pool3, 80)
    bn4    = make_batch_norm("bn4", scope, conv4, is_training)
    relu4  = make_relu("relu4", scope, bn4)

    conv5  = make_conv_3x3_no_bias("conv5", scope, relu4, 192)
    bn5    = make_batch_norm("bn5", scope, conv5, is_training)
    relu5  = make_relu("relu5", scope, bn5)
    pool5  = make_max_pool_3x3("pool5", scope, relu5)

    ############################################################################
    intnsr  = pool5
    scope  = tower_name + "/mixed_35x35x256a"
    ############################################################################

    # branch1x1
    conv6  = make_conv_1x1_no_bias("conv6", scope, intnsr, 64, padding="SAME")
    bn6    = make_batch_norm("bn6", scope, conv6, is_training)
    relu6  = make_relu("relu6", scope, bn6)

    # branch5x5
    conv7  = make_conv_1x1_no_bias("conv7", scope, intnsr, 48, padding="SAME")
    bn7    = make_batch_norm("bn7", scope, conv7, is_training)
    relu7  = make_relu("relu7", scope, bn7)
    conv8  = make_conv_5x5_no_bias("conv8", scope, relu7, 64, padding="SAME")
    bn8    = make_batch_norm("bn8", scope, conv8, is_training)
    relu8  = make_relu("relu8", scope, bn8)

    # branch3x3dbl
    conv9  = make_conv_1x1_no_bias("conv9", scope, intnsr, 64, padding="SAME")
    bn9    = make_batch_norm("bn9", scope, conv9, is_training)
    relu9  = make_relu("relu9", scope, bn9)
    conv10 = make_conv_3x3_no_bias("conv10", scope, relu9, 96, padding="SAME")
    bn10   = make_batch_norm("bn10", scope, conv10, is_training)
    relu10 = make_relu("relu10", scope, bn10)
    conv11 = make_conv_3x3_no_bias("conv11", scope, relu10, 96, padding="SAME")
    bn11   = make_batch_norm("bn11", scope, conv11, is_training)
    relu11 = make_relu("relu11", scope, bn11)

    # branch_pool
    pool12 = make_avg_pool_3x3("pool12", scope, intnsr, padding="SAME")
    conv12 = make_conv_1x1_no_bias("conv12", scope, pool12, 32, padding="SAME")
    bn12   = make_batch_norm("bn12", scope, conv12, is_training)
    relu12 = make_relu("relu12", scope, bn12)

    cc1    = tf.concat(axis=3, values=[relu6, relu8, relu11, relu12])

    ############################################################################
    intnsr = cc1
    scope  = tower_name + "/mixed_35x35x288a"
    ############################################################################

    # branch1x1
    conv13 = make_conv_1x1_no_bias("conv13", scope, intnsr, 64, padding="SAME")
    bn13   = make_batch_norm("bn13", scope, conv13, is_training)
    relu13 = make_relu("relu13", scope, bn13)

    # branch5x5
    conv14 = make_conv_1x1_no_bias("conv14", scope, intnsr, 48, padding="SAME")
    bn14   = make_batch_norm("bn14", scope, conv14, is_training)
    relu14 = make_relu("relu14", scope, bn14)
    conv15 = make_conv_5x5_no_bias("conv15", scope, relu14, 64, padding="SAME")
    bn15   = make_batch_norm("bn15", scope, conv15, is_training)
    relu15 = make_relu("relu15", scope, bn15)

    # branch3x3dbl
    conv16 = make_conv_1x1_no_bias("conv16", scope, intnsr, 64, padding="SAME")
    bn16   = make_batch_norm("bn16", scope, conv16, is_training)
    relu16 = make_relu("relu16", scope, bn16)
    conv17 = make_conv_3x3_no_bias("conv17", scope, relu16, 96, padding="SAME")
    bn17   = make_batch_norm("bn17", scope, conv17, is_training)
    relu17 = make_relu("relu17", scope, bn17)
    conv18 = make_conv_3x3_no_bias("conv18", scope, relu17, 96, padding="SAME")
    bn18   = make_batch_norm("bn18", scope, conv18, is_training)
    relu18 = make_relu("relu18", scope, bn18)

    # branch_pool
    pool19 = make_avg_pool_3x3("pool19", scope, intnsr, padding="SAME")
    conv19 = make_conv_1x1_no_bias("conv19", scope, pool19, 64, padding="SAME")
    bn19   = make_batch_norm("bn19", scope, conv19, is_training)
    relu19 = make_relu("relu19", scope, bn19)

    cc2    = tf.concat(axis=3, values=[relu13, relu15, relu18, relu19])

    ############################################################################
    intnsr = cc2
    scope  = tower_name + "/mixed_35x35x288b"
    ############################################################################

    # branch1x1
    conv20 = make_conv_1x1_no_bias("conv20", scope, intnsr, 64, padding="SAME")
    bn20   = make_batch_norm("bn20", scope, conv20, is_training)
    relu20 = make_relu("relu20", scope, bn20)

    # branch5x5
    conv21 = make_conv_1x1_no_bias("conv21", scope, intnsr, 48, padding="SAME")
    bn21   = make_batch_norm("bn21", scope, conv21, is_training)
    relu21 = make_relu("relu21", scope, bn21)
    conv22 = make_conv_5x5_no_bias("conv22", scope, relu21, 64, padding="SAME")
    bn22   = make_batch_norm("bn22", scope, conv22, is_training)
    relu22 = make_relu("relu22", scope, bn22)

    # branch3x3dbl
    conv23 = make_conv_1x1_no_bias("conv23", scope, intnsr, 64, padding="SAME")
    bn23   = make_batch_norm("bn23", scope, conv23, is_training)
    relu23 = make_relu("relu23", scope, bn23)
    conv24 = make_conv_3x3_no_bias("conv24", scope, relu23, 96, padding="SAME")
    bn24   = make_batch_norm("bn24", scope, conv24, is_training)
    relu24 = make_relu("relu24", scope, bn24)
    conv25 = make_conv_3x3_no_bias("conv25", scope, relu24, 96, padding="SAME")
    bn25   = make_batch_norm("bn25", scope, conv25, is_training)
    relu25 = make_relu("relu25", scope, bn25)

    # branch_pool
    pool26 = make_avg_pool_3x3("pool26", scope, intnsr, padding="SAME")
    conv26 = make_conv_1x1_no_bias("conv26", scope, pool26, 64, padding="SAME")
    bn26   = make_batch_norm("bn26", scope, conv26, is_training)
    relu26 = make_relu("relu26", scope, bn26)

    cc3    = tf.concat(axis=3, values=[relu20, relu22, relu25, relu26])

    ############################################################################
    intnsr = cc3
    scope  = tower_name + "/mixed_17x17x768a"
    ############################################################################

    # branch3x3
    conv27 = make_conv_3x3_stride_2_no_bias("conv27", scope, intnsr, 384)
    bn27   = make_batch_norm("bn27", scope, conv27, is_training)
    relu27 = make_relu("relu27", scope, bn27)

    # branch3x3dbl
    conv28 = make_conv_1x1_no_bias("conv28", scope, intnsr, 64, padding="SAME")
    bn28   = make_batch_norm("bn28", scope, conv28, is_training)
    relu28 = make_relu("relu28", scope, bn28)
    conv29 = make_conv_3x3_no_bias("conv29", scope, relu28, 96, padding="SAME")
    bn29   = make_batch_norm("bn29", scope, conv29, is_training)
    relu29 = make_relu("relu29", scope, bn29)
    conv30 = make_conv_3x3_stride_2_no_bias("conv30", scope, relu29, 96)
    bn30   = make_batch_norm("bn30", scope, conv30, is_training)
    relu30 = make_relu("relu30", scope, bn30)

    pool31 = make_max_pool_3x3("pool31", scope, intnsr)

    cc4    = tf.concat(axis=3, values=[relu27, relu30, pool31])

    ############################################################################
    intnsr = cc4
    scope  = tower_name + "/mixed_17x17x768b"
    ############################################################################

    # branch1x1
    conv32 = make_conv_1x1_no_bias("conv32", scope, intnsr, 192, padding="SAME")
    bn32   = make_batch_norm("bn32", scope, conv32, is_training)
    relu32 = make_relu("relu32", scope, bn32)

    # branch7x7
    conv33 = make_conv_1x1_no_bias("conv33", scope, intnsr, 128, padding="SAME")
    bn33   = make_batch_norm("bn33", scope, conv33, is_training)
    relu33 = make_relu("relu33", scope, bn33)
    conv34 = make_conv_1x7_no_bias("conv34", scope, relu33, 128, padding="SAME")
    bn34   = make_batch_norm("bn34", scope, conv34, is_training)
    relu34 = make_relu("relu34", scope, bn34)
    conv35 = make_conv_7x1_no_bias("conv35", scope, relu34, 192, padding="SAME")
    bn35   = make_batch_norm("bn35", scope, conv35, is_training)
    relu35 = make_relu("relu35", scope, bn35)

    # branch7x7dbl
    conv36 = make_conv_1x1_no_bias("conv36", scope, intnsr, 128, padding="SAME")
    bn36   = make_batch_norm("bn36", scope, conv36, is_training)
    relu36 = make_relu("relu36", scope, bn36)
    conv37 = make_conv_7x1_no_bias("conv37", scope, relu36, 128, padding="SAME")
    bn37   = make_batch_norm("bn37", scope, conv37, is_training)
    relu37 = make_relu("relu37", scope, bn37)
    conv38 = make_conv_1x7_no_bias("conv38", scope, relu37, 128, padding="SAME")
    bn38   = make_batch_norm("bn38", scope, conv38, is_training)
    relu38 = make_relu("relu38", scope, bn38)
    conv39 = make_conv_7x1_no_bias("conv39", scope, relu38, 128, padding="SAME")
    bn39   = make_batch_norm("bn39", scope, conv39, is_training)
    relu39 = make_relu("relu39", scope, bn39)
    conv40 = make_conv_1x7_no_bias("conv40", scope, relu39, 192, padding="SAME")
    bn40   = make_batch_norm("bn40", scope, conv40, is_training)
    relu40 = make_relu("relu40", scope, bn40)

    # branch_pool
    pool41 = make_avg_pool_3x3("pool41", scope, intnsr, padding="SAME")
    conv41 = make_conv_1x1_no_bias("conv41", scope, pool41, 192, padding="SAME")
    bn41   = make_batch_norm("bn41", scope, conv41, is_training)
    relu41 = make_relu("relu41", scope, bn41)

    cc5    = tf.concat(axis=3, values=[relu32, relu35, relu40, relu41])

    ############################################################################
    intnsr = cc5
    scope  = tower_name + "/mixed_17x17x768c"
    ############################################################################

    # branch1x1
    conv42 = make_conv_1x1_no_bias("conv42", scope, intnsr, 192, padding="SAME")
    bn42   = make_batch_norm("bn42", scope, conv42, is_training)
    relu42 = make_relu("relu42", scope, bn42)

    # branch7x7
    conv43 = make_conv_1x1_no_bias("conv43", scope, intnsr, 160, padding="SAME")
    bn43   = make_batch_norm("bn43", scope, conv43, is_training)
    relu43 = make_relu("relu43", scope, bn43)
    conv44 = make_conv_1x7_no_bias("conv44", scope, relu43, 160, padding="SAME")
    bn44   = make_batch_norm("bn44", scope, conv44, is_training)
    relu44 = make_relu("relu44", scope, bn44)
    conv45 = make_conv_7x1_no_bias("conv45", scope, relu44, 192, padding="SAME")
    bn45   = make_batch_norm("bn45", scope, conv45, is_training)
    relu45 = make_relu("relu45", scope, bn45)

    # branch7x7dbl
    conv46 = make_conv_1x1_no_bias("conv46", scope, intnsr, 160, padding="SAME")
    bn46   = make_batch_norm("bn46", scope, conv46, is_training)
    relu46 = make_relu("relu46", scope, bn46)
    conv47 = make_conv_7x1_no_bias("conv47", scope, relu46, 160, padding="SAME")
    bn47   = make_batch_norm("bn47", scope, conv47, is_training)
    relu47 = make_relu("relu47", scope, bn47)
    conv48 = make_conv_1x7_no_bias("conv48", scope, relu47, 160, padding="SAME")
    bn48   = make_batch_norm("bn48", scope, conv48, is_training)
    relu48 = make_relu("relu48", scope, bn48)
    conv49 = make_conv_7x1_no_bias("conv49", scope, relu48, 160, padding="SAME")
    bn49   = make_batch_norm("bn49", scope, conv49, is_training)
    relu49 = make_relu("relu49", scope, bn49)
    conv50 = make_conv_1x7_no_bias("conv50", scope, relu49, 192, padding="SAME")
    bn50   = make_batch_norm("bn50", scope, conv50, is_training)
    relu50 = make_relu("relu50", scope, bn50)

    # branch_pool
    pool51 = make_avg_pool_3x3("pool51", scope, intnsr, padding="SAME")
    conv51 = make_conv_1x1_no_bias("conv51", scope, pool51, 192, padding="SAME")
    bn51   = make_batch_norm("bn51", scope, conv51, is_training)
    relu51 = make_relu("relu51", scope, bn51)

    cc6    = tf.concat(axis=3, values=[relu42, relu45, relu50, relu51])

    ############################################################################
    intnsr = cc6
    scope  = tower_name + "/mixed_17x17x768d"
    ############################################################################

    # branch1x1
    conv52 = make_conv_1x1_no_bias("conv52", scope, intnsr, 192, padding="SAME")
    bn52   = make_batch_norm("bn52", scope, conv52, is_training)
    relu52 = make_relu("relu52", scope, bn52)

    # branch7x7
    conv53 = make_conv_1x1_no_bias("conv53", scope, intnsr, 160, padding="SAME")
    bn53   = make_batch_norm("bn53", scope, conv53, is_training)
    relu53 = make_relu("relu53", scope, bn53)
    conv54 = make_conv_1x7_no_bias("conv54", scope, relu53, 160, padding="SAME")
    bn54   = make_batch_norm("bn54", scope, conv54, is_training)
    relu54 = make_relu("relu54", scope, bn54)
    conv55 = make_conv_7x1_no_bias("conv55", scope, relu54, 192, padding="SAME")
    bn55   = make_batch_norm("bn55", scope, conv55, is_training)
    relu55 = make_relu("relu55", scope, bn55)

    # branch7x7dbl
    conv56 = make_conv_1x1_no_bias("conv56", scope, intnsr, 160, padding="SAME")
    bn56   = make_batch_norm("bn56", scope, conv56, is_training)
    relu56 = make_relu("relu56", scope, bn56)
    conv57 = make_conv_7x1_no_bias("conv57", scope, relu56, 160, padding="SAME")
    bn57   = make_batch_norm("bn57", scope, conv57, is_training)
    relu57 = make_relu("relu57", scope, bn57)
    conv58 = make_conv_1x7_no_bias("conv58", scope, relu57, 160, padding="SAME")
    bn58   = make_batch_norm("bn58", scope, conv58, is_training)
    relu58 = make_relu("relu58", scope, bn58)
    conv59 = make_conv_7x1_no_bias("conv59", scope, relu58, 160, padding="SAME")
    bn59   = make_batch_norm("bn59", scope, conv59, is_training)
    relu59 = make_relu("relu59", scope, bn59)
    conv60 = make_conv_1x7_no_bias("conv60", scope, relu59, 192, padding="SAME")
    bn60   = make_batch_norm("bn60", scope, conv60, is_training)
    relu60 = make_relu("relu60", scope, bn60)

    # branch_pool
    pool61 = make_avg_pool_3x3("pool61", scope, intnsr, padding="SAME")
    conv61 = make_conv_1x1_no_bias("conv61", scope, pool61, 192, padding="SAME")
    bn61   = make_batch_norm("bn61", scope, conv61, is_training)
    relu61 = make_relu("relu61", scope, bn61)

    cc7    = tf.concat(axis=3, values=[relu52, relu55, relu60, relu61])

    ############################################################################
    intnsr = cc7
    scope  = tower_name + "/mixed_17x17x768e"
    ############################################################################

    # branch1x1
    conv62 = make_conv_1x1_no_bias("conv62", scope, intnsr, 192, padding="SAME")
    bn62   = make_batch_norm("bn62", scope, conv62, is_training)
    relu62 = make_relu("relu62", scope, bn62)

    # branch7x7
    conv63 = make_conv_1x1_no_bias("conv63", scope, intnsr, 192, padding="SAME")
    bn63   = make_batch_norm("bn63", scope, conv63, is_training)
    relu63 = make_relu("relu63", scope, bn63)
    conv64 = make_conv_1x7_no_bias("conv64", scope, relu63, 192, padding="SAME")
    bn64   = make_batch_norm("bn64", scope, conv64, is_training)
    relu64 = make_relu("relu64", scope, bn64)
    conv65 = make_conv_7x1_no_bias("conv65", scope, relu64, 192, padding="SAME")
    bn65   = make_batch_norm("bn65", scope, conv65, is_training)
    relu65 = make_relu("relu65", scope, bn65)

    # branch7x7dbl
    conv66 = make_conv_1x1_no_bias("conv66", scope, intnsr, 192, padding="SAME")
    bn66   = make_batch_norm("bn66", scope, conv66, is_training)
    relu66 = make_relu("relu66", scope, bn66)
    conv67 = make_conv_7x1_no_bias("conv67", scope, relu66, 192, padding="SAME")
    bn67   = make_batch_norm("bn67", scope, conv67, is_training)
    relu67 = make_relu("relu67", scope, bn67)
    conv68 = make_conv_1x7_no_bias("conv68", scope, relu67, 192, padding="SAME")
    bn68   = make_batch_norm("bn68", scope, conv68, is_training)
    relu68 = make_relu("relu68", scope, bn68)
    conv69 = make_conv_7x1_no_bias("conv69", scope, relu68, 192, padding="SAME")
    bn69   = make_batch_norm("bn69", scope, conv69, is_training)
    relu69 = make_relu("relu69", scope, bn69)
    conv70 = make_conv_1x7_no_bias("conv70", scope, relu69, 192, padding="SAME")
    bn70   = make_batch_norm("bn70", scope, conv70, is_training)
    relu70 = make_relu("relu70", scope, bn70)

    # branch_pool
    pool71 = make_avg_pool_3x3("pool71", scope, intnsr, padding="SAME")
    conv71 = make_conv_1x1_no_bias("conv71", scope, pool71, 192, padding="SAME")
    bn71   = make_batch_norm("bn71", scope, conv71, is_training)
    relu71 = make_relu("relu71", scope, bn71)

    cc8    = tf.concat(axis=3, values=[relu62, relu65, relu70, relu71])

    ############################################################################
    intnsr = cc8
    scope  = tower_name + "/aux_logits"
    ############################################################################

    # aux_logits
    pool72 = make_avg_pool_5x5_stride_3("pool72", scope, intnsr)
    conv72 = make_conv_1x1_no_bias("conv72", scope, pool72, 128, padding="SAME")
    bn72   = make_batch_norm("bn72", scope, conv72, is_training)
    relu72 = make_relu("relu72", scope, bn72)

    shape  = relu72.get_shape()
    conv73 = make_conv_no_bias("conv73", scope, relu72, shape[1], shape[3], 128)
    bn73   = make_batch_norm("bn73", scope, conv73, is_training)
    relu73 = make_relu("relu73", scope, bn73)

    aux_flat   = make_flatten("aux_flatten", scope, relu73)
    aux_logits = make_fc("aux_fc", scope, aux_flat, count_classes)

    ############################################################################
    intnsr = cc8
    scope  = tower_name + "/mixed_8x8x1280a"
    ############################################################################

    # branch3x3
    conv74 = make_conv_1x1_no_bias("conv74", scope, intnsr, 192, padding="SAME")
    bn74   = make_batch_norm("bn74", scope, conv74, is_training)
    relu74 = make_relu("relu74", scope, bn74)
    conv75 = make_conv_3x3_stride_2_no_bias("conv75", scope, relu74, 320)
    bn75   = make_batch_norm("bn75", scope, conv75, is_training)
    relu75 = make_relu("relu75", scope, bn75)

    # branch7x7x3
    conv76 = make_conv_1x1_no_bias("conv76", scope, intnsr, 192, padding="SAME")
    bn76   = make_batch_norm("bn76", scope, conv76, is_training)
    relu76 = make_relu("relu76", scope, bn76)
    conv77 = make_conv_1x7_no_bias("conv77", scope, relu76, 192, padding="SAME")
    bn77   = make_batch_norm("bn77", scope, conv77, is_training)
    relu77 = make_relu("relu77", scope, bn77)
    conv78 = make_conv_7x1_no_bias("conv78", scope, relu77, 192, padding="SAME")
    bn78   = make_batch_norm("bn78", scope, conv78, is_training)
    relu78 = make_relu("relu78", scope, bn78)
    conv79 = make_conv_3x3_stride_2_no_bias("conv79", scope, relu78, 192)
    bn79   = make_batch_norm("bn79", scope, conv79, is_training)
    relu79 = make_relu("relu79", scope, bn79)

    # branch_pool
    pool80 = make_max_pool_3x3("pool80", scope, intnsr)

    cc9    = tf.concat(axis=3, values=[relu75, relu79, pool80])

    ############################################################################
    intnsr = cc9
    scope  = tower_name + "/mixed_8x8x2048a"
    ############################################################################

    # branch1x1
    conv81 = make_conv_1x1_no_bias("conv81", scope, intnsr, 320, padding="SAME")
    bn81   = make_batch_norm("bn81", scope, conv81, is_training)
    relu81 = make_relu("relu81", scope, bn81)

    # branch3x3
    conv82 = make_conv_1x1_no_bias("conv82", scope, intnsr, 384, padding="SAME")
    bn82   = make_batch_norm("bn82", scope, conv82, is_training)
    relu82 = make_relu("relu82", scope, bn82)
    conv83 = make_conv_1x3_no_bias("conv83", scope, relu82, 384, padding="SAME")
    bn83   = make_batch_norm("bn83", scope, conv83, is_training)
    relu83 = make_relu("relu83", scope, bn83)
    conv84 = make_conv_3x1_no_bias("conv84", scope, relu82, 384, padding="SAME")
    bn84   = make_batch_norm("bn84", scope, conv84, is_training)
    relu84 = make_relu("relu84", scope, bn84)
    cc10   = tf.concat(axis=3, values=[relu83, relu84])

    # branch3x3dbl
    conv85 = make_conv_1x1_no_bias("conv85", scope, intnsr, 448, padding="SAME")
    bn85   = make_batch_norm("bn85", scope, conv85, is_training)
    relu85 = make_relu("relu85", scope, bn85)
    conv86 = make_conv_3x3_no_bias("conv86", scope, relu85, 384, padding="SAME")
    bn86   = make_batch_norm("bn86", scope, conv86, is_training)
    relu86 = make_relu("relu86", scope, bn86)
    conv87 = make_conv_1x3_no_bias("conv87", scope, relu86, 384, padding="SAME")
    bn87   = make_batch_norm("bn87", scope, conv87, is_training)
    relu87 = make_relu("relu87", scope, bn87)
    conv88 = make_conv_3x1_no_bias("conv88", scope, relu86, 384, padding="SAME")
    bn88   = make_batch_norm("bn88", scope, conv88, is_training)
    relu88 = make_relu("relu88", scope, bn88)
    cc11   = tf.concat(axis=3, values=[relu87, relu88])

    # branch_pool
    pool89 = make_avg_pool_3x3("pool89", scope, intnsr, padding="SAME")
    conv89 = make_conv_1x1_no_bias("conv89", scope, pool89, 192, padding="SAME")
    bn89   = make_batch_norm("bn89", scope, conv89, is_training)
    relu89 = make_relu("relu89", scope, bn89)

    cc12   = tf.concat(axis=3, values=[relu81, cc10, cc11, relu89])

    ############################################################################
    intnsr = cc12
    scope  = tower_name + "/mixed_8x8x2048b"
    ############################################################################

    # branch1x1
    conv90 = make_conv_1x1_no_bias("conv90", scope, intnsr, 320, padding="SAME")
    bn90   = make_batch_norm("bn90", scope, conv90, is_training)
    relu90 = make_relu("relu90", scope, bn90)

    # branch3x3
    conv91 = make_conv_1x1_no_bias("conv91", scope, intnsr, 384, padding="SAME")
    bn91   = make_batch_norm("bn91", scope, conv91, is_training)
    relu91 = make_relu("relu91", scope, bn91)
    conv92 = make_conv_1x3_no_bias("conv92", scope, relu91, 384, padding="SAME")
    bn92   = make_batch_norm("bn92", scope, conv92, is_training)
    relu92 = make_relu("relu92", scope, bn92)
    conv93 = make_conv_3x1_no_bias("conv93", scope, relu91, 384, padding="SAME")
    bn93   = make_batch_norm("bn93", scope, conv93, is_training)
    relu93 = make_relu("relu93", scope, bn93)
    cc13   = tf.concat(axis=3, values=[relu92, relu93])

    # branch3x3dbl
    conv94 = make_conv_1x1_no_bias("conv94", scope, intnsr, 448, padding="SAME")
    bn94   = make_batch_norm("bn94", scope, conv94, is_training)
    relu94 = make_relu("relu94", scope, bn94)
    conv95 = make_conv_3x3_no_bias("conv95", scope, relu94, 384, padding="SAME")
    bn95   = make_batch_norm("bn95", scope, conv95, is_training)
    relu95 = make_relu("relu95", scope, bn95)
    conv96 = make_conv_1x3_no_bias("conv96", scope, relu95, 384, padding="SAME")
    bn96   = make_batch_norm("bn96", scope, conv96, is_training)
    relu96 = make_relu("relu96", scope, bn96)
    conv97 = make_conv_3x1_no_bias("conv97", scope, relu95, 384, padding="SAME")
    bn97   = make_batch_norm("bn97", scope, conv97, is_training)
    relu97 = make_relu("relu97", scope, bn97)
    cc14   = tf.concat(axis=3, values=[relu96, relu97])

    # branch_pool
    pool98 = make_avg_pool_3x3("pool98", scope, intnsr, padding="SAME")
    conv98 = make_conv_1x1_no_bias("conv98", scope, pool98, 192, padding="SAME")
    bn98   = make_batch_norm("bn98", scope, conv98, is_training)
    relu98 = make_relu("relu98", scope, bn98)

    cc15   = tf.concat(axis=3, values=[relu90, cc13, cc14, relu98])

    ############################################################################
    intnsr = cc15
    scope  = tower_name + "/logits"
    ############################################################################

    shape  = intnsr.get_shape()
    pool99 = make_avg_pool("pool99", scope, intnsr, shape[1], shape[3])
    do99   = make_dropout("do99", scope, pool99, keep_prob)

    flat   = make_flatten("flatten", scope, do99)
    logits = make_fc("fc", scope, flat, count_classes)

    for var in tf.trainable_variables():
        tf.summary.histogram(var.op.name, var)

    with tf.name_scope(tower_name + "/loss"):
        y_out     = tf.stop_gradient(y_out)
        aux_preds = lsr_loss(aux_logits, y_out, 0.1, 0.4)
        preds     = lsr_loss(logits, y_out, 0.1, 1.0)
        loss      = tf.reduce_mean(aux_preds+preds)
    return logits, preds, loss


def run_towers(keep_prob, is_training,
        training_data, validation_data, count_classes):
    with tf.device("/device:CPU:0"), tf.name_scope("input/train_or_eval"):
        images, labels = \
            tf.cond(is_training, lambda: training_data, lambda: validation_data)
        images_1, images_2 = tf.split(images, num_or_size_splits=2)
        labels_1, labels_2 = tf.split(labels, num_or_size_splits=2)
    with tf.device("/device:GPU:0"):
        logits1, preds1, loss1 = make_tower("tower1",
            images_1, labels_1, keep_prob, is_training, count_classes)
    with tf.device("/device:GPU:1"):
        logits2, preds2, loss2 = make_tower("tower2",
            images_2, labels_2, keep_prob, is_training, count_classes)
    with tf.device("/device:GPU:1"),\
            tf.name_scope("metrics/concat_tower_outputs"):
        logits     = tf.concat([logits1, logits2], 0)
    return loss1, loss2, logits, labels


def apply_gradients(loss1, loss2, global_step, trainer):
    with tf.device("/device:GPU:0"), tf.name_scope("tower1/compute_grads"):
        grads1 = trainer.compute_gradients(loss1)
    with tf.device("/device:GPU:1"), tf.name_scope("tower2/compute_grads"):
        grads2 = trainer.compute_gradients(loss2)
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    with tf.control_dependencies(update_ops):
        with tf.device("/device:GPU:0"), tf.name_scope("merge_grads"):
            grads   = average_gradients([grads1, grads2])
        with tf.device("/device:CPU:0"), tf.name_scope("apply_grads"):
            applied = trainer.apply_gradients(grads, global_step)
    return applied


def compute_total_loss(loss1, loss2):
    with tf.device("/device:GPU:1"), tf.name_scope("loss"):
        return tf.reduce_mean([loss1, loss2], 0)


def evaluate_validation(logits, labels):
    with tf.device("/device:GPU:1"), tf.name_scope("metrics"):
        labels = tf.argmax(labels, 1)
        in_top_1 = tf.nn.in_top_k(logits, labels, 1)
        in_top_5 = tf.nn.in_top_k(logits, labels, 5)
        acc_top_1 = tf.reduce_mean(tf.cast(in_top_1, tf.float32))
        acc_top_5 = tf.reduce_mean(tf.cast(in_top_5, tf.float32))
        return acc_top_1, acc_top_5
